from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from util.langchain import AgentState
from util.logging import logger

from agents.director.prompt import system_prompt
from agents.director.schema.schema import (
    DirectorState,
    IntentLlmResponse,
    Question,
    QuestionLlmResponse,
)
from agents.scriptwriter.graph import async_call_model as scriptwriter_call_model
from agents.scriptwriter.schema import ActingScriptSchema

model = ChatOpenAI(model="gpt-4o-mini", temperature=1.2)


async def classify_intent(state: DirectorState):
    logger.info("> Classify intent START")
    response = await model.with_structured_output(IntentLlmResponse).ainvoke(
        input=[
            SystemMessage(content=system_prompt["intent"]["v1"]),
            AIMessage(content=state["messages"][-2].content),
            HumanMessage(content=state["messages"][-1].content),
        ]
    )
    state["user_intent"] = response.intent
    logger.info(f"> Classify intent END: {state['user_intent']}")
    return state


async def question(state: DirectorState):
    logger.info("> Question START")
    response = await model.with_structured_output(QuestionLlmResponse).ainvoke(
        input=[SystemMessage(content=system_prompt["question"]["v1"])]
        + state["messages"],
    )
    question: Question = response.question
    message = AIMessage(content=question.message)
    logger.info(f"> Question END: {question.model_dump_json()}")
    return {
        "messages": [message],
        "question": question,
    }


async def script(state: DirectorState, config: RunnableConfig):
    logger.info("> Write script START")
    agent_state: AgentState = await scriptwriter_call_model(state, config)
    logger.info(
        f"> agent_state['messages'][-1].content: {agent_state['messages'][-1].content}"
    )
    acting_script: ActingScriptSchema = ActingScriptSchema.from_json_string(
        agent_state["messages"][-1].content
    )
    message = AIMessage(content=acting_script.to_script_message())
    logger.info(f"> Write script END: {message.content}")
    return {"messages": [message], "script": acting_script}


def route_to_next_node(state: DirectorState) -> str:
    logger.info(f">> Route to next node START intent: {state['user_intent']}")
    if (
        state["user_intent"] == "Acceptance [FINAL OUTPUT]"
        or state["user_intent"] == "Just do it"
    ):
        if state.get("script"):
            logger.info(f">> Route to next node FINAL SCRIPT: {state['script']}")
            return "END"
        else:
            logger.info(">> Route to next node: script_agent")
            return "script_agent"
    if state["user_intent"] == "Stop":
        logger.info(">> Route to next node: script_agent")
        return "script_agent"
    logger.info(">> Route to next node: question_agent")
    return "question_agent"


def create_director_agent(checkpointer=None):
    workflow = StateGraph(state_schema=DirectorState)

    workflow.add_node("intent_agent", classify_intent)
    workflow.add_node("script_agent", script)
    workflow.add_node("question_agent", question)

    workflow.add_edge(START, "intent_agent")

    workflow.add_conditional_edges(
        "intent_agent",
        route_to_next_node,
        {
            "question_agent": "question_agent",
            "script_agent": "script_agent",
            "END": END,
        },
    )

    workflow.add_edge("script_agent", END)
    workflow.add_edge("question_agent", END)

    compiled = workflow.compile(checkpointer=checkpointer, name="director")

    return compiled
