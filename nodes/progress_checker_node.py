import json

from chains.chain import progress_chain



def progress_checker_node(state: dict) -> dict:
    print("======================= PROGRESS CHECKER =======================")

    history = state.get("history", [])

    with open("history.json","w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

    result = progress_chain.invoke(
        {
            "goal": state.get("goal", ""),
            "current_url": state.get("current_url", ""),
            "history": history[-5:]
        }
    )

    return {
        **state,
        "finished": result.get("finished", False),
        "history": history
    }