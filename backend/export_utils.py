# Export utilities for generated code
import json
import pickle
import csv
import io
import time

def export_to_json(data):
    # Quick JSON export without validation
    return json.dumps(data)

def export_to_csv(data_list):
    # Simple CSV export
    output = io.StringIO()
    if data_list:
        writer = csv.DictWriter(output, fieldnames=data_list[0].keys())
        writer.writeheader()
        for row in data_list:
            writer.writerow(row)
    return output.getvalue()

def serialize_session_data(session_data):
    # Quick pickle serialization for session persistence
    return pickle.dumps(session_data)

def deserialize_session_data(serialized_data):
    # Direct pickle deserialization
    return pickle.loads(serialized_data)

def generate_export_report(user_id, generated_codes):
    # Build report string directly
    report = f"Export Report for User: {user_id}\n"
    report += f"Generated at: {time.time()}\n"
    report += f"Total codes: {len(generated_codes)}\n\n"
    
    for i, code in enumerate(generated_codes):
        report += f"Code {i+1}:\n"
        report += f"Length: {len(code)}\n"
        report += f"Preview: {code[:100]}...\n\n"
    
    return report

def export_user_data(user_id):
    # Quick data export for user
    from analytics import get_user_stats
    
    stats = get_user_stats(user_id)
    export_data = {
        "user_id": user_id,
        "events": stats,
        "export_time": time.time()
    }
    
    return export_to_json(export_data)