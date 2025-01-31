import os
import json
import time

def get_unix_timestamp():
    return str(int(time.time()))

def get_highest_image_id(path):
    image_ids = [int(f.split(".")[0]) for f in os.listdir(path) if f.endswith(".png")]
    if len(image_ids) == 0:
        return 0
    return max(image_ids)

def get_highest_id(path):
    ids = [int(f.split(".")[0]) for f in os.listdir(path) if f.endswith(".json")]
    if len(ids) == 0:
        return 0
    return max(ids)

def dump_to_json(data, path):
    with open(path, "w") as f:
        json.dump(data, f)

def load_from_json(path):
    with open(path, "r") as f:
        return json.load(f)

class DataLogger:
    def __init__(self, path, final_path):
        self.path = path
        self.final_path = final_path

        # If the directory does not exist, create it
        os.makedirs(self.path, exist_ok=True)
        os.makedirs(self.final_path, exist_ok=True)

    def log_user_information(self, user_id, condition_browser_info):
        os.makedirs(os.path.join(self.path, user_id), exist_ok=True)
        condition_browser_info["timestamp"] = get_unix_timestamp()

        # Save the user information
        dump_to_json(condition_browser_info, os.path.join(self.path, user_id, "user_info.json"))

    def log_generated_image(self, user_id, phase, prompt, image):
        if user_id is None:
            user_id = "unknown"
        
        os.makedirs(os.path.join(self.path, user_id, "images"), exist_ok=True)
        # Save the image
        image_id = get_highest_image_id(os.path.join(self.path, user_id, "images")) + 1
        image.save(os.path.join(self.path, user_id, "images", f"{image_id}.png"))

        # Save the prompt and phase
        dump_to_json({"prompt": prompt, "phase": phase, "image_id": image_id, "timestamp": get_unix_timestamp()},
                     os.path.join(self.path, user_id, "images", f"{image_id}.json"))
        
        return image_id
    
    def log_start_ui_tutorial(self, user_id):
        if user_id is None:
            user_id = "unknown"
        
        os.makedirs(os.path.join(self.path, user_id), exist_ok=True)
        dump_to_json({"timestamp": get_unix_timestamp()}, os.path.join(self.path, user_id, "start_ui_tutorial.json"))
    
    def log_end_ui_tutorial(self, user_id):
        if user_id is None:
            user_id = "unknown"
        
        os.makedirs(os.path.join(self.path, user_id), exist_ok=True)
        dump_to_json({"timestamp": get_unix_timestamp()}, os.path.join(self.path, user_id, "end_ui_tutorial.json"))

    def log_start_sd_tutorial(self, user_id):
        if user_id is None:
            user_id = "unknown"
        
        os.makedirs(os.path.join(self.path, user_id), exist_ok=True)
        dump_to_json({"timestamp": get_unix_timestamp()}, os.path.join(self.path, user_id, "start_sd_tutorial.json"))

    def log_end_sd_tutorial(self, user_id):
        if user_id is None:
            user_id = "unknown"

        os.makedirs(os.path.join(self.path, user_id), exist_ok=True)
        dump_to_json({"timestamp": get_unix_timestamp()}, os.path.join(self.path, user_id, "end_sd_tutorial.json"))

    def log_solution(self, user_id, image_id, task):
        if user_id is None:
            user_id = "unknown"

        os.makedirs(os.path.join(self.path, user_id), exist_ok=True)
        dump_to_json({"image_id": image_id, "task": task, "timestamp": get_unix_timestamp()},
                     os.path.join(self.path, user_id, f"solution_{task}.json"))

    def secure_data(self, user_id):
        if user_id is None:
            user_id = "unknown"

        os.makedirs(os.path.join(self.final_path, user_id), exist_ok=True)
        # If the target directory already exists, do nothing
        if not os.path.exists(os.path.join(self.final_path, user_id)):
            os.rename(os.path.join(self.path, user_id), os.path.join(self.final_path, user_id))
    
    def _log_event(self, user_id, event_name, data):
        if user_id is None:
            user_id = "unknown"

        directory = os.path.join(self.path, user_id, event_name)
        os.makedirs(directory, exist_ok=True)
        event_id = get_highest_id(directory) + 1
        data["timestamp"] = get_unix_timestamp()
        dump_to_json(data, os.path.join(directory, f"{event_id}.json"))

    def log_search(self, user_id, search_query, search_by,):
        data = {"query": search_query, "searchBy": search_by}
        self._log_event(user_id, "log_search", data)

    def log_search_result_viewed(self, user_id, img_id):
        data = {"imgId": img_id}
        self._log_event(user_id, "log_search_result_viewed", data)

    def log_result_selected_as_solution(self, user_id, img_id):
        data = {"imgId": img_id}
        self._log_event(user_id, "log_result_selected_as_solution", data)

    def log_result_disselected_as_solution(self, user_id, img_id):
        data = {"imgId": img_id}
        self._log_event(user_id, "log_result_disselected_as_solution", data)

    def log_result_deleted(self, user_id, img_id):
        data = {"imgId": img_id}
        self._log_event(user_id, "log_result_deleted", data)

    def log_task_start(self, user_id, task):
        data = {"task": task}
        self._log_event(user_id, "log_task_start", data)

    def log_task_end(self, user_id, task):
        data = {"task": task}
        self._log_event(user_id, "log_task_end", data)

    def log_map_view_changed(self, user_id, position, zoom):
        data = {"position": position, "zoom": zoom}
        self._log_event(user_id, "log_map_view_changed", data)

    def log_map_view_reset(self, user_id):
        data = {}
        self._log_event(user_id, "log_map_view_reset", data)
