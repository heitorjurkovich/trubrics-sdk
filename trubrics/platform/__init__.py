from typing import Optional

from loguru import logger

from trubrics.platform.auth import expire_after_n_seconds, get_trubrics_auth_token
from trubrics.platform.config import TrubricsConfig, TrubricsDefaults
from trubrics.platform.feedback import Feedback, Response
from trubrics.platform.firestore import (
    get_trubrics_firestore_api_url,
    list_components_in_organisation,
    list_projects_in_organisation,
    save_document_to_collection,
)
from trubrics.platform.prompts import ModelConfig, Prompt


class Trubrics:
    def __init__(
        self,
        email: str,
        password: str,
        project: str,
        firebase_api_key: Optional[str] = None,
        firebase_project_id: Optional[str] = None,
    ):
        if firebase_api_key or firebase_project_id:
            if firebase_api_key and firebase_project_id:
                defaults = TrubricsDefaults(firebase_api_key=firebase_api_key, firebase_project_id=firebase_project_id)
            else:
                raise ValueError("Both API key and firebase_project_id are required to change project.")
        else:
            defaults = TrubricsDefaults()

        auth = get_trubrics_auth_token(defaults.firebase_api_key, email, password, rerun=expire_after_n_seconds())
        if "error" in auth:
            raise Exception(f"Error in login email '{email}' to the Trubrics UI: {auth['error']}")
        else:
            firestore_api_url = get_trubrics_firestore_api_url(auth, defaults.firebase_project_id)

        projects = list_projects_in_organisation(firestore_api_url, auth)
        if project not in projects:
            raise KeyError(f"Project '{project}' not found. Please select one of {projects}.")

        self.config = TrubricsConfig(
            email=email,
            password=password,  # type: ignore
            project=project,
            username=auth["displayName"],
            firebase_api_key=defaults.firebase_api_key,
            firestore_api_url=firestore_api_url,
        )

    def log_prompt(
        self,
        model_config: ModelConfig,
        prompt: str,
        generation: str,
        user_id: Optional[str] = None,
        tags: list = [],
        metadata: dict = {},
    ) -> Optional[Prompt]:
        prompt = Prompt(
            model_config=model_config,
            prompt=prompt,
            generation=generation,
            user_id=user_id,
            tags=tags,
            metadata=metadata,
        )
        auth = get_trubrics_auth_token(
            self.config.firebase_api_key,
            self.config.email,
            self.config.password.get_secret_value(),
            rerun=expire_after_n_seconds(),
        )
        res = save_document_to_collection(
            auth,
            firestore_api_url=self.config.firestore_api_url,
            project=self.config.project,
            collection="prompts",
            document=prompt,
        )
        if "error" in res:
            logger.error(res["error"])
            return None
        else:
            logger.info("Feedback response saved to Trubrics.")
            prompt.id = res["name"].split("/")[-1]
            return prompt

    def log_feedback(
        self,
        component: str,
        model: str,
        user_response: Response,
        prompt_id: Optional[str] = None,
        user_id: Optional[str] = None,
        tags: list = [],
        metadata: dict = {},
    ) -> Optional[Feedback]:
        """
        Log user feedback to Trubrics.
        """
        feedback = Feedback(
            component=component,
            model=model,
            user_response=user_response,
            prompt_id=prompt_id,
            user_id=user_id,
            tags=tags,
            metadata=metadata,
        )
        auth = get_trubrics_auth_token(
            self.config.firebase_api_key,
            self.config.email,
            self.config.password.get_secret_value(),
            rerun=expire_after_n_seconds(),
        )
        components = list_components_in_organisation(
            firestore_api_url=self.config.firestore_api_url, auth=auth, project=self.config.project
        )
        if feedback.component not in components:
            raise ValueError(f"Component '{feedback.component}' not found. Please select one of: {components}.")
        res = save_document_to_collection(
            auth,
            firestore_api_url=self.config.firestore_api_url,
            project=self.config.project,
            collection=f"feedback/{feedback.component}/responses",
            document=feedback,
        )
        if "error" in res:
            logger.error(res["error"])
            return None
        else:
            logger.info("Feedback response saved to Trubrics.")
            return feedback
