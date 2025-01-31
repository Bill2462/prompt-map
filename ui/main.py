import io
import traceback
import logging
import threading
from functools import wraps
from flask import Flask, send_from_directory, request, jsonify, send_file, redirect

# Import your application-specific modules
from app import Ui
from app.util import pil_to_base64
from app.img_db import ImageDatabase
from app.diffusion_db import DiffusionDb
from app.sd_model import get_sd_model
from app.configs import Paths, AppConfig
from app.text_embedding_model import TextEmbeddingModelSt
from app.task_order_selector import OrderSelector
from app.data_logger import DataLogger

sem_sd_generation = threading.Semaphore()
sem_search = threading.Semaphore()

# Setup logging configuration
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s [%(levelname)s] %(message)s',
                    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()])

logger = logging.getLogger(__name__)

# Initialize your components
paths = Paths.from_json("cfg/paths.json")
config = AppConfig.from_json("cfg/config.json")
task_order_selector = OrderSelector(paths.logdir)
data_logger = DataLogger(paths.logdir, paths.final_logdir)

text_embedding_model = TextEmbeddingModelSt(paths.sentence_transformer_model_path, "cpu")

ui = Ui(paths, config, text_embedding_model)
ui.text_embedding_model = text_embedding_model

diffusion_db = DiffusionDb(text_embedding_model,
                           paths.diffusion_db_search_index_path,
                           paths.diffusion_db_path)

prompt_map_img_db = ImageDatabase(paths.main_img_db_path)
diffusion_db_img_db = ImageDatabase(paths.diffusiondb_img_db_path, img_size=512)

sd_model = get_sd_model(paths.sd_path, config.use_dummy_sd_model)

logger.info("Components loaded!")

app = Flask(__name__, static_folder="static")

def handle_exceptions(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error("Exception: %s", e, exc_info=True)
            traceback.print_exc()
            return jsonify({"result": "error", "message": str(e)})
    return decorated_function

# Webpages
@app.route("/", methods=["GET"])
def index():
    logger.info('Serving index page')
    return send_from_directory("static/html", "index.html")

@app.route("/conditions/brightEinstein", methods=["GET"])
def condition_1():
    p_id = request.args.get("prolificPid")
    data_logger.log_end_ui_tutorial(p_id)
    logger.info('Serving brightEinstein condition page for prolificPid: %s', p_id)
    return send_from_directory("static/html", "condition_1.html")

@app.route("/conditions/blueCuttlefish", methods=["GET"])
def condition_2():
    p_id = request.args.get("prolificPid")
    data_logger.log_end_ui_tutorial(p_id)
    logger.info('Serving blueCuttlefish condition page for prolificPid: %s', p_id)
    return send_from_directory("static/html", "condition_2.html")

@app.route("/conditions/goldenDragon", methods=["GET"])
def condition_3():
    p_id = request.args.get("prolificPid")
    data_logger.log_end_ui_tutorial(p_id)
    logger.info('Serving goldenDragon condition page for prolificPid: %s', p_id)
    return send_from_directory("static/html", "condition_3.html")

@app.route("/start", methods=["GET"])
def start():
    prolific_pid = request.args.get("PROLIFIC_PID")
    first_task = task_order_selector.get_first_task()
    response = send_from_directory("static/html", "start.html")

    response.set_cookie("prolificPid", prolific_pid)
    response.set_cookie("condition", config.condition)
    response.set_cookie("firstTask", str(first_task))
    response.set_cookie("firstTaskDone", "false")

    if config.condition == "brightEinstein":
        response.set_cookie("youtubeUrl", "https://www.youtube.com/embed/UZwhX-fOZIY")
    elif config.condition == "blueCuttlefish":
        response.set_cookie("youtubeUrl", "https://www.youtube.com/embed/JE78yZ9dji4")
    elif config.condition == "goldenDragon":
        response.set_cookie("youtubeUrl", "https://www.youtube.com/embed/OLRc7Ql-xzQ")
    else:
        logger.error('Invalid condition: %s', config.condition)
        raise Exception("Invalid condition")

    logger.info('Serving start page for prolificPid: %s with condition: %s', prolific_pid, config.condition)
    return response

@app.route("/sdTutorial", methods=["GET"])
def sdTutorial():
    p_id = request.args.get("prolificPid")
    data_logger.log_start_sd_tutorial(p_id)
    logger.info('Serving sd_tutorial page for prolificPid: %s', p_id)
    return send_from_directory("static/html", "sd_tutorial.html")

@app.route("/uiTutorial", methods=["GET"])
def ui_tutorial():
    p_id = request.args.get("prolificPid")
    data_logger.log_start_ui_tutorial(p_id)
    data_logger.log_end_sd_tutorial(p_id)
    logger.info('Serving ui_tutorial page for prolificPid: %s', p_id)
    return send_from_directory("static/html", "ui_tutorial.html")

@app.route("/terminateStudy", methods=["GET"])
def terminate_study():
    p_id = request.args.get("prolificPid")
    data_logger.secure_data(p_id)
    logger.info('Terminating study for prolificPid: %s', p_id)
    return redirect(f"https://tuwien193.qualtrics.com/jfe/form/SV_7NHcFi2byYAdDTw?PROLIFIC_PID={p_id}")

# API
@app.route("/api/map/labels/general")
def get_general_labels():
    output = ui.get_general_labels()
    logger.info('Retrieving general labels')
    return jsonify({"result": "ok", "data": [label.to_dict() for label in output]})

@app.route("/api/map/labels/detailed", methods=["GET"])
@handle_exceptions
def get_detailed_labels():
    level = request.args.get("level")
    origin_x_start = request.args.get("originXStart")
    origin_x_end = request.args.get("originXEnd")
    origin_y_start = request.args.get("originYStart")
    origin_y_end = request.args.get("originYEnd")

    logger.info('Retrieving detailed labels for level: %s, origin_x: (%s,%s), origin_y: (%s,%s)',
                level, origin_x_start, origin_x_end, origin_y_start, origin_y_end)

    output = ui.get_detailed_labels((float(origin_x_start), float(origin_x_end)),
                                    (float(origin_y_start), float(origin_y_end)),
                                    level)

    return jsonify({"result": "ok", "data": [label.to_dict() for label in output]})

@app.route("/api/map/points", methods=["GET"])
@handle_exceptions
def get_map_points():
    origin_x_start = request.args.get("originXStart")
    origin_x_end = request.args.get("originXEnd")
    origin_y_start = request.args.get("originYStart")
    origin_y_end = request.args.get("originYEnd")

    logger.info('Retrieving map points for origin_x: (%s,%s), origin_y: (%s,%s)',
                origin_x_start, origin_x_end, origin_y_start, origin_y_end)

    output = ui.get_map_points((float(origin_x_start), float(origin_x_end)),
                               (float(origin_y_start), float(origin_y_end)))

    output = [point.to_dict() for point in output]
    return jsonify({"result": "ok", "data": output})

@app.route("/api/map/imagePreview", methods=["GET"])
@handle_exceptions
def get_map_image_preview():
    origin_x_start = request.args.get("originXStart")
    origin_x_end = request.args.get("originXEnd")
    origin_y_start = request.args.get("originYStart")
    origin_y_end = request.args.get("originYEnd")
    mapLevel = request.args.get("level")

    logger.info('Retrieving map image preview for level: %s, origin_x: (%s,%s), origin_y: (%s,%s)',
                mapLevel, origin_x_start, origin_x_end, origin_y_start, origin_y_end)

    output = ui.get_preview_images((float(origin_x_start), float(origin_x_end)),
                                   (float(origin_y_start), float(origin_y_end)),
                                    mapLevel)

    output = [point.to_dict() for point in output]
    return jsonify({"result": "ok", "data": output})

@app.route("/api/getImage", methods=["GET"])
@handle_exceptions
def get_image():
    fname = request.args.get("fname")
    # Skip logging for this endpoint
    output = prompt_map_img_db.get_img(fname)

    img_byte_arr = io.BytesIO()
    output.save(img_byte_arr, format="JPEG")
    img_byte_arr.seek(0)

    return send_file(img_byte_arr, mimetype='image/jpeg')

@app.route("/api/diffusiondb/getImage", methods=["GET"])
@handle_exceptions
def get_image_diffusion_db():
    fname = request.args.get("fname")
    logger.info('Retrieving diffusion db image for fname: %s', fname)
    output = diffusion_db_img_db.get_img(fname)

    img_byte_arr = io.BytesIO()
    output.save(img_byte_arr, format="JPEG")
    img_byte_arr.seek(0)

    return send_file(img_byte_arr, mimetype='image/jpeg')

@app.route("/api/makeImage", methods=["GET"])
@handle_exceptions
def make_image_prompt_map():
    sem_sd_generation.acquire()
    prompt = request.args.get("prompt")
    phase = request.args.get("phase")
    p_id = request.args.get("prolificPid")
    logger.info('Generating image for prompt: %s, phase: %s, prolificPid: %s', prompt, phase, p_id)
    output = sd_model.generate_img(prompt)[0]
    image_id = data_logger.log_generated_image(p_id, phase, prompt, output)
    sem_sd_generation.release()
    return jsonify({"result": "ok", "data": pil_to_base64(output), "imageId": image_id})

@app.route("/api/search/promptMap", methods=["GET"])
@handle_exceptions
def search_prompt_map():
    sem_search.acquire()
    querry = request.args.get("querry")
    index_name = request.args.get("searchBy")
    n_points = request.args.get("nPoints")

    logger.info('Searching prompt map for query: %s, search_by: %s, n_points: %s',
                querry, index_name, n_points)

    outputs = ui.search_by_txt(index_name, querry, int(n_points))
    sem_search.release()
    return jsonify({"result": "ok", "data": [point.to_dict() for point in outputs]})

@app.route("/api/diffusiondb/search", methods=["GET"])
@handle_exceptions
def search_diffusiondb():
    sem_search.acquire()
    query = request.args.get("querry")
    n_points = request.args.get("nPoints")

    logger.info('Searching diffusion db for query: %s, n_points: %s',
                query, n_points)

    output = diffusion_db.search_by_txt(query, int(n_points))
    outs = []
    for o in output:
        outs.append({"id": o["index"], "prompt": o["prompt"]})

    sem_search.release()
    return jsonify({"result": "ok", "data": outs})

# APIs for logging user interactions, solution and TLX results
@app.route("/api/log/userInfo", methods=["POST"])
@handle_exceptions
def log_user_info():
    data = request.json
    data_logger.log_user_information(data["prolificPid"], data)
    logger.info('Logging user information for prolificPid: %s', data["prolificPid"])
    return jsonify({"result": "ok"})

@app.route("/api/log/interaction", methods=["POST"])
@handle_exceptions
def log_interaction():
    data = request.json
    ui.log_interaction(data)
    logger.info('Logging interaction for prolificPid: %s', data["prolificPid"])
    return jsonify({"result": "ok"})

@app.route("/api/log/solution", methods=["POST"])
@handle_exceptions
def log_solution():
    data = request.json
    data_logger.log_solution(data["prolificPid"], data["imgId"], data["task"])
    logger.info('Logging solution for prolificPid: %s, imgId: %s, task: %s',
                data["prolificPid"], data["imgId"], data["task"])
    return jsonify({"result": "ok"})

@app.route("/api/log/search", methods=["POST"])
@handle_exceptions
def log_search():
    data = request.json
    data_logger.log_search(data["prolificPid"], data["searchQuerry"], data["searchBy"])
    logger.info('Logging search for prolificPid: %s, search_query: %s, search_by: %s',
                data["prolificPid"], data["searchQuerry"], data["searchBy"])
    return jsonify({"result": "ok"})

@app.route("/api/log/searchResultViewed", methods=["POST"])
@handle_exceptions
def log_search_result_viewed():
    data = request.json
    data_logger.log_search_result_viewed(data["prolificPid"], data["imgId"])
    logger.info('Logging search result viewed for prolificPid: %s, imgId: %s',
                data["prolificPid"], data["imgId"])
    return jsonify({"result": "ok"})

@app.route("/api/log/resultSelectedAsSolution", methods=["POST"])
@handle_exceptions
def log_result_selected_as_solution():
    data = request.json
    data_logger.log_result_selected_as_solution(data["prolificPid"], data["imgId"])
    logger.info('Logging result selected as solution for prolificPid: %s, imgId: %s',
                data["prolificPid"], data["imgId"])
    return jsonify({"result": "ok"})

@app.route("/api/log/resultDisselectedAsSolution", methods=["POST"])
@handle_exceptions
def log_result_disselected_as_solution():
    data = request.json
    data_logger.log_result_disselected_as_solution(data["prolificPid"], data["imgId"])
    logger.info('Logging result disselected as solution for prolificPid: %s, imgId: %s',
                data["prolificPid"], data["imgId"])
    return jsonify({"result": "ok"})

@app.route("/api/log/resultDeleted", methods=["POST"])
@handle_exceptions
def log_result_deleted():
    data = request.json
    data_logger.log_result_deleted(data["prolificPid"], data["imgId"])
    logger.info('Logging result deleted for prolificPid: %s, imgId: %s',
                data["prolificPid"], data["imgId"])
    return jsonify({"result": "ok"})

@app.route("/api/log/taskStart", methods=["POST"])
@handle_exceptions
def log_task_start():
    data = request.json
    data_logger.log_task_start(data["prolificPid"], data["task"])
    logger.info('Logging task start for prolificPid: %s, task: %s',
                data["prolificPid"], data["task"])
    return jsonify({"result": "ok"})

@app.route("/api/log/taskEnd", methods=["POST"])
@handle_exceptions
def log_task_end():
    data = request.json
    data_logger.log_task_end(data["prolificPid"], data["task"])
    logger.info('Logging task end for prolificPid: %s, task: %s',
                data["prolificPid"], data["task"])
    return jsonify({"result": "ok"})

@app.route("/api/log/mapViewReset", methods=["POST"])
@handle_exceptions
def log_map_view_reset():
    data = request.json
    data_logger.log_map_view_reset(data["prolificPid"])
    logger.info('Logging map view reset for prolificPid: %s', data["prolificPid"])
    return jsonify({"result": "ok"})

@app.route("/api/log/mapViewChanged", methods=["POST"])
@handle_exceptions
def log_map_view_changed():
    data = request.json
    data_logger.log_map_view_changed(data["prolificPid"], data["position"], data["zoom"])
    logger.info('Logging map view changed for prolificPid: %s, position: %s, zoom: %s',
                data["prolificPid"], data["position"], data["zoom"])
    return jsonify({"result": "ok"})

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8000)
