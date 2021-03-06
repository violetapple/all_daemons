import aiohttp_jinja2
import aiohttp
import asyncio
from asyncio.subprocess import create_subprocess_exec, PIPE
import pickle
import logging
import copy

FILE_FOR_LOG = u"logs.log"
bash_command = ["service"]


def log(message, type_of_log):
    logging.basicConfig(format=u'%(levelname)-8s [%(asctime)s] %(message)s',
                        level=logging.DEBUG, filename=FILE_FOR_LOG)
    if type_of_log == "debug":
        logging.debug(message)
    elif type_of_log == "error":
        logging.error(message)
    else:
        logging.info(message)


def get_process(commands):
    return create_subprocess_exec(*commands, stdout=PIPE, stderr=PIPE)

async def get_daemons_list():
    try:
        daemons = {}
        command_list = ["sudo", "service", "--status-all"]
        process = await get_process(command_list)
        output, err = await process.communicate()
        lines = bytes(output).decode().split('\n')
        for line in lines:
            if len(line) == 0:
                break
            name = line.split(']  ')[1]
            if '+' in line:
                daemons[name] = '+'
            else:
                daemons[name] = '-'
    except Exception as e:
        print("Exception occured while getting list of daemons")
        print(e)
    return daemons


async def perform_and_check(command_list):
    lock = asyncio.Lock()
    try:
        with (await lock):
            process = await get_process(command_list)
            output, err = await process.communicate()
        if output:
            log("Success. Return code of terminating process: " +
                str(process.returncode), "debug")
            log("Success. Output: " + "\n" + bytes(output).decode(),
                "debug")
        if err:
            log("Error. Return code of terminating process: " +
                str(process.returncode), "error")
            log("Error. Information: " + bytes(err).decode(),
                "error")
    except Exception as e:
        output = ""
        err = ""
        log("Exception occured while trying to terminate process: " +
            "\n", "error")
        log(e, "error")
    return output, err


async def is_daemon_running(daemon_name):
    full_bash_command = ["ps", "-e"]
    output, err = await perform_and_check(full_bash_command)
    if daemon_name in bytes(output).decode():
        return True
    return False


async def handle(command, daemon_name):
    full_bash_command = copy.copy(bash_command)
    full_bash_command.append(daemon_name)
    full_bash_command.append(command)
    state_dict = {"start": True, "stop": False}
    if command != "restart":
        if state_dict[command] == await is_daemon_running(daemon_name):
            return
        else:
            await perform_and_check(full_bash_command)
    await perform_and_check(full_bash_command)


async def start_daemon(daemon_name):
    await handle("start", daemon_name)


async def stop_daemon(daemon_name):
    await handle("stop", daemon_name)


async def restart_daemon(daemon_name):
    await handle("restart", daemon_name)


def update_checkbox_value(host_ip, checked):
    checkbox_dict = {}
    dump_file = "checkbox.pickle"
    with open(dump_file, "rb") as f:
        try:
            checkbox_dict = pickle.load(f)
            if not isinstance(checkbox_dict, dict):
                    checkbox_dict = {host_ip: checked}
            else:
                checkbox_dict[host_ip] = checked
        except Exception as e:
            log("Exception while serializing checkbox", "error")
            log(e, "error")
            checkbox_dict = {host_ip: checked}
    with open(dump_file, "wb") as f:
        pickle.dump(checkbox_dict, f)


def get_checkbox_value(host_ip):
    checkbox_dict = {}
    dump_file = "checkbox.pickle"
    failed_to_load = False
    try:
        with open(dump_file, "rb") as f:
            checkbox_dict = pickle.load(f)
            if not isinstance(checkbox_dict, dict):
                checkbox_dict[host_ip] = True
    except Exception as e:
        checkbox_dict[host_ip] = True
    return checkbox_dict[host_ip]


@aiohttp_jinja2.template('base.html')
async def index(request):
    log("Got GET from client", "debug")
    peername = request.transport.get_extra_info('peername')
    if peername is not None:
        host_ip, port = peername
    checked = True
    checked = get_checkbox_value(host_ip)
    daemons = await get_daemons_list()
    return {"checked": checked, "daemons": daemons}


async def save_checkbox(request):
    log("Saving checkbox state", "debug")
    checkbox_data = {}
    checkbox_data = await request.json()
    checked = checkbox_data["checked"]
    peername = request.transport.get_extra_info("peername")
    if peername is not None:
        host_ip, port = peername
    update_checkbox_value(host_ip, checked)
    return aiohttp.web.json_response({"checked": checked})


async def change_daemon(request):
    peername = request.transport.get_extra_info("peername")
    if peername is not None:
        host_ip, port = peername
    checked = get_checkbox_value(host_ip)
    message = ""
    action_type = {}
    try:
        action_type = await request.json()
    except Exception as e:
        log("Exception while receiving json", "error")
        log(e, "error")
    if action_type["start"]:
        await start_daemon(action_type["name"])
        log("daemon has started", "debug")
    elif action_type["restart"]:
        await restart_daemon(action_type["name"])
        log("daemon has restarted", "debug")
    elif action_type["stop"]:
        await stop_daemon(action_type["name"])
        log("daemon has stopped", "debug")
    state = await is_daemon_running(action_type["name"])
    if state:
        message = {"state": "+"}
    else:
        message = {"state": "-"}
    message["name"] = action_type["name"]
    return aiohttp.web.json_response(message)

