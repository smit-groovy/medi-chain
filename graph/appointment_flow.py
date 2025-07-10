from langgraph.graph import StateGraph, END
from pydantic import BaseModel
from agent.medical_agent import get_medical_explainer
from utils.appointments import save_appointment


class AppointmentState(BaseModel):
    user: str
    doctor: str
    symptoms: str
    datetime: str
    wallet: str
    explanation: str = ""
    cid: str = ""


def get_graph_chain():
    graph = StateGraph(state_schema=AppointmentState)

    # Node 1: (Unused node — placeholder)
    def ask_symptoms(state: AppointmentState):
        return {}

    # Node 2: AI explanation
    def ai_explainer_node(state: AppointmentState):
        chain = get_medical_explainer()
        result = chain.invoke(state.symptoms)
        explanation = result.content if hasattr(result, "content") else str(result)
        return {"explanation": explanation.strip()}

    # Node 3: Save and upload to IPFS
    def confirm_and_save(state: AppointmentState):
        appointment = {
            "user": state.user,
            "doctor": state.doctor,
            "symptoms": state.symptoms,
            "datetime": state.datetime,
            "explanation": state.explanation,
        }

        try:
            cid = save_appointment(wallet=state.wallet, **appointment)
            return {"cid": cid}
        except Exception as e:
            print("⚠️ IPFS Upload Failed:", e)
            return {"cid": "Upload failed"}

    # Build graph
    graph.add_node("ask_symptoms", ask_symptoms)
    graph.add_node("ai_explainer", ai_explainer_node)
    graph.add_node("confirm_save", confirm_and_save)

    graph.set_entry_point("ask_symptoms")
    graph.add_edge("ask_symptoms", "ai_explainer")
    graph.add_edge("ai_explainer", "confirm_save")
    graph.add_edge("confirm_save", END)

    return graph.compile()


def run_appointment_chain(state_dict: dict):
    graph = get_graph_chain()
    return graph.invoke(state_dict)
