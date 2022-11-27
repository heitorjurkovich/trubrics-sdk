import gradio as gr

from trubrics.feedback import config
from trubrics.feedback.dataclass import Feedback


def collect_feedback_gradio(path: str, file_name=None, tags=None, metadata=None):
    """
    Gets feedback from the user and saves it in the path given through the input through gradio web user interface.
    Feedback can be in the form of text or any other format. If no path is given, it saves it in the default working directory.
    
    Args:
        path : The path where the feedback file gets saved. If empty, defaults to current working directory.
        file_name: Name of the file. If Empty,defaults to "Feedback.json".
        metadata: Any other form of metric which the user wants to log into the feedback file such as feature value,prediction,etc. If empty,defaults to None.
        tags: list of any tags for this feedback file. If empty, defaults to None.

    """
    def get_feedback(title: str, description: str):
        if not (len(title) == 0 or len(description) == 0):
            feedback = Feedback(title=title, description=description, tags=tags, metadata=metadata)
            feedback.save_local(path=path, file_name=file_name)
            return config.FEEDBACK_SAVED_HTML
        else:
            return config.FEEDBACK_NOT_SAVED_HTML

    title = gr.Textbox(label=config.TITLE, placeholder=config.TITLE_EXPLAIN)
    description = gr.Textbox(label=config.DESCRIPTION, placeholder=config.DESCRIPTION_EXPLAIN, lines=5)
    feedback_button = gr.Button(config.FEEDBACK_SAVE_BUTTON)
    kwargs = {"fn": get_feedback, "inputs": [title, description], "outputs": gr.HTML()}
    return feedback_button.click(**kwargs)
