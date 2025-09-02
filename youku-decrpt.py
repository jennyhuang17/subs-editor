from pywidevine.cdm import Cdm
from pywidevine.device import Device
from pywidevine.pssh import PSSH
import requests
import base64

pssh = input("PSSH? ")
pssh = PSSH(pssh)
lic_url = 'https://drm-license.youku.tv/ups/drm.json'

device = Device.load("YOURDEVICE.wvd")
cdm = Cdm.from_device(device)
session_id = cdm.open()
challenge = cdm.get_license_challenge(session_id, pssh)

challenge = {
  'drmType': 'widevine',
  'token': '0MN6i1W4qAq5bNnu3OyRdKA_z8JUHK2s8LPY6AgUW3RF0E_MafKtXL_Wg-fAC2PDh0UIQsWSZBK_bmH7Rg5YrhjmVmqhFZ6C',
  'vid': 'XNjQ1MTI1MTA2OA==',
  'psid': '7ffb556d5a11768a79c165fb4200b7fd41346',
  'ccode': '0597',
  'licenseRequest': base64.b64encode(challenge).decode()
}

licence = requests.post(lic_url, data=challenge)
cdm.parse_license(session_id, licence.json()['data'])
for key in cdm.get_keys(session_id):
    if key.type=='CONTENT':
        print(f"\n--key {key.kid.hex}:{key.key.hex()}")
cdm.close(session_id)