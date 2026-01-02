# comms/csv_receiver.py
import csv
import os
from config import CSV_READ_EXISTING


class CSVReceiver:
    def __init__(self, csv_path, packet_handler, queue_manager):
        self.csv_path = csv_path
        self.packet_handler = packet_handler
        self.queue_manager = queue_manager

        if CSV_READ_EXISTING:
            # Read from beginning (existing + new rows)
            self.last_line_read = 0
        else:
            # Ignore existing rows, read only future rows
            self.last_line_read = self._count_existing_rows()

    # --------------------------------------------------
    # POLL CSV FOR NEW ENTRIES (NON-BLOCKING)
    # --------------------------------------------------
    def poll(self):
        """
        Reads new rows from CSV file and pushes valid packets into queue.
        This function is SAFE to call repeatedly in main loop.
        """

        if not os.path.exists(self.csv_path):
            return  # CSV not yet created

        try:
            with open(self.csv_path, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                rows = list(reader)

                # Process only new rows
                new_rows = rows[self.last_line_read:]

                for row in new_rows:
                    print("📄 CSV row read:", row)
                    
                    raw_packet = self._row_to_packet(row)

                    if raw_packet is None:
                        continue

                    clean_packet = self.packet_handler.validate(raw_packet)

                    if clean_packet:
                        self.queue_manager.add_packet(clean_packet)
                        print(f"📥 CSV packet accepted: {clean_packet['id']}")

                self.last_line_read = len(rows)

        except Exception as e:
            # Never crash mission due to CSV issues
            print(f"⚠️ CSV read error: {e}")

    # --------------------------------------------------
    # CONVERT CSV ROW TO RAW PACKET
    # --------------------------------------------------
    def _row_to_packet(self, row):
        """
        Converts CSV row dict to raw packet dict.
        Returns None if row is malformed.
        """

#        try:
#            return {
#                "id": row["id"],
#                "lat": row["lat"],
#                "lon": row["lon"],
#                "alt": row["alt"],
#                "confidence": row["confidence"],
#                "timestamp": row["timestamp"]
#            }
#        except KeyError:
#            return None
        try:
            return {
                "id": int(row["id"]),
                "lat": float(row["lat"]),
                "lon": float(row["lon"]),
                "alt": float(row["alt"]),
                "confidence": float(row["confidence"]),
                "timestamp": float(row["timestamp"])
            }
        except (KeyError, ValueError):
            return None


 
 
 
    # --------------------------------------------------
    # COUNT EXISTING CSV ROWS
    # --------------------------------------------------
    def _count_existing_rows(self):
        if not os.path.exists(self.csv_path):
            return 0

        try:
            with open(self.csv_path, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                return len(list(reader))
        except Exception:
            return 0

