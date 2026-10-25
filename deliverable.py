"""
Video Content Library Module

This module provides a clean, modular, and production-ready implementation for managing
a video content library. It allows adding, retrieving, searching, and listing video content
metadata. This implementation is pure Python, has zero external dependencies, and is suitable
for integration into the bujiproject-art/agentmidasopendevteam project.

Author: [Your Name]
Date: 2024-06-13
"""

from typing import List, Dict, Optional


class VideoContent:
    """
    Represents a single video content item in the library.
    """

    def __init__(
        self,
        video_id: str,
        title: str,
        description: str,
        url: str,
        tags: Optional[List[str]] = None,
        duration_seconds: Optional[int] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Initialize a VideoContent instance.

        Args:
            video_id (str): Unique identifier for the video.
            title (str): Title of the video.
            description (str): Description of the video.
            url (str): URL to access the video.
            tags (Optional[List[str]]): List of tags associated with the video.
            duration_seconds (Optional[int]): Duration of the video in seconds.
            metadata (Optional[Dict[str, str]]): Additional metadata as key-value pairs.
        """
        self.video_id = video_id
        self.title = title
        self.description = description
        self.url = url
        self.tags = tags or []
        self.duration_seconds = duration_seconds
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, object]:
        """
        Convert the VideoContent instance to a dictionary.

        Returns:
            Dict[str, object]: Dictionary representation of the video content.
        """
        return {
            "video_id": self.video_id,
            "title": self.title,
            "description": self.description,
            "url": self.url,
            "tags": self.tags,
            "duration_seconds": self.duration_seconds,
            "metadata": self.metadata,
        }


class VideoContentLibrary:
    """
    Manages a collection of VideoContent items.
    """

    def __init__(self) -> None:
        """
        Initialize the VideoContentLibrary.
        """
        self._videos: Dict[str, VideoContent] = {}

    def add_video(self, video: VideoContent) -> bool:
        """
        Add a new video to the library.

        Args:
            video (VideoContent): The video content to add.

        Returns:
            bool: True if added successfully, False if video_id already exists.
        """
        if video.video_id in self._videos:
            return False
        self._videos[video.video_id] = video
        return True

    def get_video(self, video_id: str) -> Optional[VideoContent]:
        """
        Retrieve a video by its ID.

        Args:
            video_id (str): The unique identifier of the video.

        Returns:
            Optional[VideoContent]: The video content if found, else None.
        """
        return self._videos.get(video_id)

    def list_videos(self) -> List[VideoContent]:
        """
        List all videos in the library.

        Returns:
            List[VideoContent]: List of all video content items.
        """
        return list(self._videos.values())

    def search_videos(
        self,
        query: str,
        tags: Optional[List[str]] = None,
        min_duration: Optional[int] = None,
        max_duration: Optional[int] = None,
    ) -> List[VideoContent]:
        """
        Search for videos by title/description and optional filters.

        Args:
            query (str): Search string for title or description.
            tags (Optional[List[str]]): List of tags to filter by (all must match).
            min_duration (Optional[int]): Minimum duration in seconds.
            max_duration (Optional[int]): Maximum duration in seconds.

        Returns:
            List[VideoContent]: List of matching video content items.
        """
        results: List[VideoContent] = []
        query_lower = query.lower()
        for video in self._videos.values():
            if (
                query_lower in video.title.lower()
                or query_lower in video.description.lower()
            ):
                if tags:
                    if not all(tag in video.tags for tag in tags):
                        continue
                if min_duration is not None:
                    if video.duration_seconds is None or video.duration_seconds < min_duration:
                        continue
                if max_duration is not None:
                    if video.duration_seconds is None or video.duration_seconds > max_duration:
                        continue
                results.append(video)
        return results

    def remove_video(self, video_id: str) -> bool:
        """
        Remove a video from the library by its ID.

        Args:
            video_id (str): The unique identifier of the video to remove.

        Returns:
            bool: True if removed successfully, False if not found.
        """
        if video_id in self._videos:
            del self._videos[video_id]
            return True
        return False


# --- TESTS ---

def _run_tests() -> None:
    """
    Run basic tests for the VideoContentLibrary.
    """
    library = VideoContentLibrary()

    # Add videos
    video1 = VideoContent(
        video_id="vid001",
        title="Introduction to Python",
        description="A beginner's guide to Python programming.",
        url="https://example.com/python-intro",
        tags=["python", "beginner", "programming"],
        duration_seconds=600,
    )
    video2 = VideoContent(
        video_id="vid002",
        title="Advanced Python",
        description="Deep dive into advanced Python topics.",
        url="https://example.com/python-advanced",
        tags=["python", "advanced"],
        duration_seconds=1200,
    )
    assert library.add_video(video1) is True
    assert library.add_video(video2) is True
    assert library.add_video(video1) is False  # Duplicate

    # Get video
    assert library.get_video("vid001") is video1
    assert library.get_video("vid999") is None

    # List videos
    all_videos = library.list_videos()
    assert len(all_videos) == 2

    # Search videos
    results = library.search_videos("python")
    assert len(results) == 2

    results = library.search_videos("beginner")
    assert len(results) == 1
    assert results[0].video_id == "vid001"

    results = library.search_videos("python", tags=["advanced"])
    assert len(results) == 1
    assert results[0].video_id == "vid002"

    results = library.search_videos("python", min_duration=1000)
    assert len(results) == 1
    assert results[0].video_id == "vid002"

    # Remove video
    assert library.remove_video("vid001") is True
    assert library.get_video("vid001") is None
    assert library.remove_video("vid001") is False

    print("All VideoContentLibrary tests passed.")


if __name__ == "__main__":
    _run_tests()