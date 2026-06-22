# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from question_bank_generator_base import *  # noqa: F403,E402


def _mod_cg0_0():
    return {
        "coding_fundamentals": {
                "junior": [
                    {
                        "question": "Write a function to reverse a string without using built-in reverse methods.",
                        "competency": "coding_fundamentals",
                        "type": "coding",
                        "difficulty": "easy",
                        "time_limit": 15,
                        "key_concepts": ["loops", "string_manipulation", "basic_algorithms"]
                    },
                    {
                        "question": "Implement a function to check if a string is a palindrome.",
                        "competency": "coding_fundamentals", 
                        "type": "coding",
                        "difficulty": "easy",
                        "time_limit": 15,
                        "key_concepts": ["string_processing", "comparison", "edge_cases"]
                    },
                    {
                        "question": "Find the largest element in an array without using built-in max functions.",
                        "competency": "coding_fundamentals",
                        "type": "coding", 
                        "difficulty": "easy",
                        "time_limit": 10,
                        "key_concepts": ["arrays", "iteration", "comparison"]
                    }
                ],
                "mid": [
                    {
                        "question": "Implement a function to find the first non-repeating character in a string.",
                        "competency": "coding_fundamentals",
                        "type": "coding",
                        "difficulty": "medium",
                        "time_limit": 20,
                        "key_concepts": ["hash_maps", "string_processing", "efficiency"]
                    },
                    {
                        "question": "Write a function to merge two sorted arrays into one sorted array.",
                        "competency": "coding_fundamentals",
                        "type": "coding",
                        "difficulty": "medium", 
                        "time_limit": 25,
                        "key_concepts": ["merge_algorithms", "two_pointers", "optimization"]
                    }
                ],
                "senior": [
                    {
                        "question": "Implement a LRU (Least Recently Used) cache with O(1) operations.",
                        "competency": "coding_fundamentals",
                        "type": "coding",
                        "difficulty": "hard",
                        "time_limit": 35,
                        "key_concepts": ["data_structures", "hash_maps", "doubly_linked_lists"]
                    }
                ]
            },
        "system_design": {
                "mid": [
                    {
                        "question": "Design a URL shortener service like bit.ly for 10K users.",
                        "competency": "system_design",
                        "type": "design",
                        "difficulty": "medium",
                        "time_limit": 45,
                        "key_concepts": ["database_design", "hashing", "basic_scalability"]
                    }
                ],
                "senior": [
                    {
                        "question": "Design a real-time chat system supporting 1M concurrent users.",
                        "competency": "system_design",
                        "type": "design",
                        "difficulty": "hard",
                        "time_limit": 60,
                        "key_concepts": ["websockets", "load_balancing", "database_sharding", "caching"]
                    },
                    {
                        "question": "Design a distributed cache system like Redis with high availability.",
                        "competency": "system_design",
                        "type": "design",
                        "difficulty": "hard",
                        "time_limit": 60,
                        "key_concepts": ["distributed_systems", "replication", "consistency", "partitioning"]
                    }
                ],
                "staff": [
                    {
                        "question": "Design the architecture for a global content delivery network (CDN).",
                        "competency": "system_design",
                        "type": "design",
                        "difficulty": "expert",
                        "time_limit": 75,
                        "key_concepts": ["global_architecture", "edge_computing", "content_optimization", "network_protocols"]
                    }
                ]
            },
    }
