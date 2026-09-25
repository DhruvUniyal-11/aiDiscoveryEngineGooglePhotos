"""
Repository pattern for Evidence Record storage using SQLite and JSONL export.
Handles persistence, query, serialization, and deserialization of 19-field EvidenceRecord instances.
"""

import json
import sqlite3
from pathlib import Path
from typing import List, Optional, Union
from src.models.evidence import EvidenceRecord
from src.models.taxonomy import (
    FailureStage,
    FailureCategory,
    MemoryClueType,
    PhotoEventuallyFound,
    EvidenceStrength,
    ClaimTag,
)


class EvidenceRepository:
    def __init__(self, db_path: Union[str, Path] = ":memory:"):
        self.db_path = str(db_path)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS evidence_records (
                    evidence_id TEXT PRIMARY KEY,
                    source_platform TEXT NOT NULL,
                    source_url TEXT NOT NULL,
                    source_date TEXT NOT NULL,
                    user_quote TEXT NOT NULL,
                    user_intent TEXT NOT NULL,
                    remembered_clues TEXT NOT NULL,  -- JSON Array
                    forgotten_clues TEXT NOT NULL,   -- JSON Array
                    query_attempted TEXT NOT NULL,
                    search_strategy TEXT NOT NULL,
                    outcome_description TEXT NOT NULL,
                    perceived_failure_reason TEXT NOT NULL,
                    photo_eventually_found TEXT NOT NULL,
                    workaround_used TEXT NOT NULL,
                    emotional_behavioral_consequence TEXT NOT NULL,
                    failure_stage INTEGER NOT NULL,
                    failure_category TEXT NOT NULL,
                    underlying_user_need TEXT NOT NULL,
                    evidence_strength TEXT NOT NULL,
                    notes TEXT NOT NULL,
                    claim_tag TEXT NOT NULL,
                    memory_clue_type INTEGER
                )
            """)
            conn.commit()

    def save_record(self, record: EvidenceRecord) -> str:
        """
        Saves or updates an EvidenceRecord in the SQLite database.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO evidence_records (
                    evidence_id, source_platform, source_url, source_date, user_quote,
                    user_intent, remembered_clues, forgotten_clues, query_attempted,
                    search_strategy, outcome_description, perceived_failure_reason,
                    photo_eventually_found, workaround_used, emotional_behavioral_consequence,
                    failure_stage, failure_category, underlying_user_need, evidence_strength,
                    notes, claim_tag, memory_clue_type
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(evidence_id) DO UPDATE SET
                    source_platform=excluded.source_platform,
                    source_url=excluded.source_url,
                    source_date=excluded.source_date,
                    user_quote=excluded.user_quote,
                    user_intent=excluded.user_intent,
                    remembered_clues=excluded.remembered_clues,
                    forgotten_clues=excluded.forgotten_clues,
                    query_attempted=excluded.query_attempted,
                    search_strategy=excluded.search_strategy,
                    outcome_description=excluded.outcome_description,
                    perceived_failure_reason=excluded.perceived_failure_reason,
                    photo_eventually_found=excluded.photo_eventually_found,
                    workaround_used=excluded.workaround_used,
                    emotional_behavioral_consequence=excluded.emotional_behavioral_consequence,
                    failure_stage=excluded.failure_stage,
                    failure_category=excluded.failure_category,
                    underlying_user_need=excluded.underlying_user_need,
                    evidence_strength=excluded.evidence_strength,
                    notes=excluded.notes,
                    claim_tag=excluded.claim_tag,
                    memory_clue_type=excluded.memory_clue_type
            """, (
                record.evidence_id,
                record.source_platform,
                record.source_url,
                record.source_date,
                record.user_quote,
                record.user_intent,
                json.dumps(record.remembered_clues),
                json.dumps(record.forgotten_clues),
                record.query_attempted,
                record.search_strategy,
                record.outcome_description,
                record.perceived_failure_reason,
                record.photo_eventually_found.value,
                record.workaround_used,
                record.emotional_behavioral_consequence,
                int(record.failure_stage),
                record.failure_category.value,
                record.underlying_user_need,
                record.evidence_strength.value,
                record.notes,
                record.claim_tag.value,
                int(record.memory_clue_type) if record.memory_clue_type else None,
            ))
            conn.commit()
            return record.evidence_id

    def get_record(self, evidence_id: str) -> Optional[EvidenceRecord]:
        """
        Fetches an EvidenceRecord by evidence_id.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM evidence_records WHERE evidence_id = ?", (evidence_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return self._row_to_record(row)

    def get_all_records(self) -> List[EvidenceRecord]:
        """
        Fetches all EvidenceRecords stored in the repository.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM evidence_records ORDER BY evidence_id ASC")
            rows = cursor.fetchall()
            return [self._row_to_record(r) for r in rows]

    def count_records(self) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM evidence_records")
            return cursor.fetchone()[0]

    def clear_all(self) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM evidence_records")
            conn.commit()

    def _row_to_record(self, row: sqlite3.Row) -> EvidenceRecord:
        return EvidenceRecord(
            evidence_id=row["evidence_id"],
            source_platform=row["source_platform"],
            source_url=row["source_url"],
            source_date=row["source_date"],
            user_quote=row["user_quote"],
            user_intent=row["user_intent"],
            remembered_clues=json.loads(row["remembered_clues"]),
            forgotten_clues=json.loads(row["forgotten_clues"]),
            query_attempted=row["query_attempted"],
            search_strategy=row["search_strategy"],
            outcome_description=row["outcome_description"],
            perceived_failure_reason=row["perceived_failure_reason"],
            photo_eventually_found=PhotoEventuallyFound(row["photo_eventually_found"]),
            workaround_used=row["workaround_used"],
            emotional_behavioral_consequence=row["emotional_behavioral_consequence"],
            failure_stage=FailureStage(row["failure_stage"]),
            failure_category=FailureCategory(row["failure_category"]),
            underlying_user_need=row["underlying_user_need"],
            evidence_strength=EvidenceStrength(row["evidence_strength"]),
            notes=row["notes"],
            claim_tag=ClaimTag(row["claim_tag"]),
            memory_clue_type=MemoryClueType(row["memory_clue_type"]) if row["memory_clue_type"] else None,
        )

    def export_to_jsonl(self, filepath: Union[str, Path]) -> Path:
        target = Path(filepath)
        target.parent.mkdir(parents=True, exist_ok=True)
        records = self.get_all_records()
        with open(target, "w", encoding="utf-8") as f:
            for rec in records:
                f.write(rec.model_dump_json() + "\n")
        return target

    def import_from_jsonl(self, filepath: Union[str, Path]) -> int:
        target = Path(filepath)
        if not target.exists():
            raise FileNotFoundError(f"JSONL file not found: {target}")
        count = 0
        with open(target, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                data = json.loads(line)
                rec = EvidenceRecord.model_validate(data)
                self.save_record(rec)
                count += 1
        return count

    def export_to_json(self, filepath: Union[str, Path]) -> Path:
        target = Path(filepath)
        target.parent.mkdir(parents=True, exist_ok=True)
        records = self.get_all_records()
        data = [rec.model_dump(mode="json") for rec in records]
        with open(target, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return target
