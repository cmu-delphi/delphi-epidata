# standard library
import os.path
import subprocess
import json

def dangerously_simulate_api_response(request_dict):
  """*SHOULD NOT RECEIVE USER INPUT*.  Simulates the API output for the specified request using server files located within this repository's directory structure.

  The request should be in the form of a dictionary specifying the html query parameters / php $_REQUEST entries for the request.  Used to construct tests of API behavior.  *Security note*: the request argument should not be supplied by an outside user, only carefully specified during development, or usage thoroughly vetted, as, depending on usage (pre-deploy, during deploy, post-deploy), potential risks may vary.

  The API output is simulated using files from ../../src/server/ in this repository's directory structure.  No web requests are issued, nor (when run on the server) does it use the currently deployed version of the API.

  Returns a tuple (returncode, stderr_bytes, stdout_bytes).
  """
  request_json = json.dumps(request_dict)
  process = subprocess.Popen(
    cwd=os.path.join(os.path.dirname(os.path.realpath(__file__)),'..','..','src','server'),
    args=['php', '-r', '$_REQUEST = json_decode(file_get_contents("php://stdin"), true); require("api.php");'],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
  )
  (stdout_bytes, stderr_bytes) = process.communicate(input=request_json.encode('UTF-8'))
  returncode = process.returncode
  simulated_api_response = (returncode, stderr_bytes, stdout_bytes)
  return simulated_api_response

def extract_response_json(simulated_api_response):
  (returncode, stderr_bytes, stdout_bytes) = simulated_api_response
  if returncode != 0 or len(stderr_bytes)!=0:
    raise Exception(['Simulated API request appears to have generated an internal error, returning a nonzero error code and/or producing output to stderr:',returncode,stderr_bytes])
  else:
    unpacked_json = json.loads(stdout_bytes.decode("UTF-8"))
    return unpacked_json
