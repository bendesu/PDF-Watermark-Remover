import os
from app_test.pypdf_EncodedStreamObject import testing as test_encoded
from app_test.pypdf_with_link import testing as test_pypdf_with_link


default_failed_folder = "app_test/failed_files"
default_test_file_folder = "app_test/test_files"


def init(failed_folder):
  abspath = os.path.abspath(__file__)
  os.chdir(os.path.dirname(abspath))
  if not os.path.exists(failed_folder):
    os.makedirs(failed_folder)
  for f in os.listdir(failed_folder):
    os.remove(os.path.join(failed_folder, f))

def unit_test(data):
  success = True
  try:
    test_func = data[-1]
    path_to_test_file = os.path.join(default_test_file_folder, data[0])
    rs = test_func(path_to_test_file)
    assert rs[0].hexdigest() == data[1]
    print(f"\n- Passed assessment against '{data[2]}'.\n")
  except Exception:
    success = False
    path_to_failed_file = os.path.join(default_failed_folder, f"failed_{data[0]}")
    with open(path_to_failed_file, "wb") as f:
      f.write(rs[1])
    print(f"\n- Failed assessment for '{data[2]}'")
    print(f"- Please check the output file: '{path_to_failed_file}'\n")
  finally:
    return success

if __name__ == '__main__':
  init(default_failed_folder)

  data_list = [
    # test_file_name, MD5_value_of_the_test_result, test_description, test_func
    ("test_file_1.pdf", "fc29f72b62cfabbcd3987c529dfca4f6", "EncodedStreamObject", test_encoded),
    ("test_file_2.pdf", "4870f29aea309da415e6d1ba2ed28c93", "pypdf watermark removal with links", test_pypdf_with_link),

  ]

  fail_num = 0
  total = 0

  for data in data_list:
    success = unit_test(data)
    if not success:
      fail_num += 1
    total +=1
    
  print(f"> Total tested: {total}")
  print(f"> Failed tests: {fail_num}\n")