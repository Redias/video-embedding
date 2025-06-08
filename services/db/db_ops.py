#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
sqlite operations for video embeddings.
'''

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
from utils import Logger

logger = Logger()

class VideoEmbeddingDB:
    def __init__(self, db_path: str = "video_embeddings.db"):
        """初始化数据库连接
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        try:
            self._init_db()
            logger.info(f"数据库连接成功: {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"数据库连接失败: {e}")
            raise

    def _init_db(self):
        """初始化数据库表结构"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        
        try:
            # 创建视频信息表
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS videos (
                    video_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_path TEXT UNIQUE NOT NULL,
                    duration FLOAT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 创建帧信息表
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS frame_embeddings (
                    frame_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_id INTEGER,
                    start_time FLOAT,
                    end_time FLOAT,
                    frame_embedding BLOB,
                    text_transcription TEXT,
                    FOREIGN KEY (video_id) REFERENCES videos(video_id)
                )
            """)
            
            self.conn.commit()
            logger.info("数据库表结构初始化完成")
        except sqlite3.Error as e:
            logger.error(f"数据库表创建失败: {e}")
            raise

    def add_video(self, video_path: str, duration: float) -> int:
        """添加视频信息"""
        try:
            self.cursor.execute(
                "INSERT INTO videos (video_path, duration) VALUES (?, ?)",
                (str(video_path), duration)
            )
            self.conn.commit()
            video_id = self.cursor.lastrowid
            logger.info(f"添加视频成功: {video_path} (ID: {video_id})")
            return video_id
        except sqlite3.IntegrityError:
            # 如果视频已存在，返回已存在的video_id
            self.cursor.execute("SELECT video_id FROM videos WHERE video_path = ?", (str(video_path),))
            video_id = self.cursor.fetchone()[0]
            logger.info(f"视频已存在: {video_path} (ID: {video_id})")
            return video_id
        except sqlite3.Error as e:
            logger.error(f"添加视频失败: {e}")
            raise

    def add_frame_embedding(self, video_id: int, frame_data: Dict[str, Any]):
        """添加帧embedding信息"""
        try:
            frame_embedding_bytes = frame_data['frame_embedding'].tobytes()
            
            self.cursor.execute("""
                INSERT INTO frame_embeddings 
                (video_id, start_time, end_time, frame_embedding, text_transcription)
                VALUES (?, ?, ?, ?, ?)
            """, (
                video_id,
                frame_data['start_time'],
                frame_data['end_time'],
                frame_embedding_bytes,
                frame_data['text_transcription']
            ))
            self.conn.commit()
            logger.info(f"添加帧embedding成功: video_id={video_id}, time={frame_data['start_time']:.2f}")
        except sqlite3.Error as e:
            logger.error(f"添加帧embedding失败: {e}")
            raise
        except KeyError as e:
            logger.error(f"帧数据格式错误: {e}")
            raise

    def get_frame_embeddings(self, video_id: int) -> List[Dict[str, Any]]:
        """获取视频的所有帧embedding信息"""
        try:
            self.cursor.execute("""
                SELECT start_time, end_time, frame_embedding, text_transcription 
                FROM frame_embeddings 
                WHERE video_id = ? 
                ORDER BY start_time
            """, (video_id,))
            
            results = []
            for row in self.cursor.fetchall():
                frame_embedding = np.frombuffer(row[2], dtype=np.float32)
                results.append({
                    'start_time': row[0],
                    'end_time': row[1],
                    'frame_embedding': frame_embedding,
                    'text_transcription': row[3]
                })
            logger.info(f"获取帧embedding成功: video_id={video_id}, count={len(results)}")
            return results
        except sqlite3.Error as e:
            logger.error(f"获取帧embedding失败: {e}")
            raise

    def close(self):
        """关闭数据库连接"""
        if self.conn:
            try:
                self.conn.close()
                logger.info("数据库连接已关闭")
            except sqlite3.Error as e:
                logger.error(f"关闭数据库连接失败: {e}")
