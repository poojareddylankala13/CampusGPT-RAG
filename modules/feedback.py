import logging

from modules.database import add_feedback as db_add_feedback

logger = logging.getLogger("CampusGPT.feedback")


def submit_feedback(chat_id, user_id, rating, comments=None):
    """Submits user feedback for a specific chat response.

    Args:
        chat_id (int): The chat history entry ID.
        user_id (int): The ID of the user submitting feedback.
        rating (str): 'helpful' or 'not_helpful'.
        comments (str, optional): Additional text feedback.

    Returns:
        bool: True if feedback was successfully submitted, else False.
    """
    logger.info(f"Submitting feedback for chat {chat_id} by user {user_id}: {rating}")

    if rating not in ["helpful", "not_helpful"]:
        logger.error(f"Invalid rating type: {rating}")
        return False

    try:
        db_add_feedback(chat_id, user_id, rating, comments)
        return True
    except Exception as e:
        logger.error(f"Failed to submit feedback: {str(e)}")
        return False
