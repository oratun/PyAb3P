import csv
import ctypes
import logging
import multiprocessing
import os
import traceback
from ctypes import Structure, c_char_p, c_double, c_int
from typing import List

logger = logging.Logger(name=__name__)


class AbbrOut(Structure):
    _fields_ = [
        ("sf", c_char_p),
        ("lf", c_char_p),
        ("strat", c_char_p),
        ("sf_offset", c_int),
        ("lf_offset", c_int),
        ("prec", c_double),
    ]


class AbbrExtractor:
    def __init__(self):
        self.libAb3PWrapper = ctypes.CDLL("libAb3PWrapper.so")
        # Create Ab3PWrapper instance
        create_ab3p = self.libAb3PWrapper.create_ab3p
        create_ab3p.restype = ctypes.c_void_p
        self.ab3p_instance = create_ab3p()
        self.add_text = self.libAb3PWrapper.add_text
        self.add_text.argtypes = [ctypes.c_void_p, ctypes.c_char_p]

        self.get_abbrs = self.libAb3PWrapper.get_abbrs
        self.get_abbrs.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(AbbrOut),
            ctypes.POINTER(ctypes.c_int),
        ]
        self.get_abbrs.restype = None

    def close(self):
        # Destroy Ab3PWrapper instance
        destroy_ab3p = self.libAb3PWrapper.destroy_ab3p
        destroy_ab3p.argtypes = [ctypes.c_void_p]
        destroy_ab3p(self.ab3p_instance)

    def get_abbrs_from_line(self, text: str, max_ct=100) -> List[dict]:
        # Add text
        self.add_text(self.ab3p_instance, text.encode())

        abbrs_count = ctypes.c_int(max_ct)
        abbrs = (AbbrOut * abbrs_count.value)()
        self.get_abbrs(self.ab3p_instance, abbrs, ctypes.byref(abbrs_count))

        result = []
        for i in range(abbrs_count.value):
            try:
                result.append(
                    {
                        "sf": abbrs[i].sf.decode(errors="ignore"),
                        "lf": abbrs[i].lf.decode(errors="ignore"),
                        "sf_offset": abbrs[i].sf_offset,
                        "lf_offset": abbrs[i].lf_offset,
                        "prec": abbrs[i].prec,
                    }
                )
            except IndexError:
                pass
        return result


def get_abbrs_from_pmc(abs_file: str, result_file: str, suffix=""):
    logger.info(f"starting get_abbrs_from_pmc")
    write_header = False if os.path.exists(result_file) else True
    with open(result_file, "a", newline="") as csv_file:
        f = csv.writer(csv_file)
        if write_header:
            f.writerow(["pmc_id", "sf", "lf", "sf_offset", "lf_offset", "prec"])
        ae = AbbrExtractor()
        with open(abs_file) as f2:
            reader = csv.DictReader(f2)
            csv.field_size_limit(5000000)
            for idx, row in enumerate(reader):
                abstract_id = row["pmc_id"]

                logger.info(f"{idx=}, {abstract_id=}")
                try:
                    results = ae.get_abbrs_from_line(row["content"])
                except:
                    results = []
                if not results:
                    continue
                rows = [
                    [
                        abstract_id,
                        i["sf"],
                        i["lf"],
                        i["sf_offset"],
                        i["lf_offset"],
                        i["prec"],
                    ]
                    for i in results
                ]
                f.writerows(rows)
        # ae.close()


def run_function_in_subprocess(func, timeout=300, *args, **kwargs):
    def wrapper(queue, *args, **kwargs):
        try:
            result = func(*args, **kwargs)
            queue.put((True, result))
        except Exception as e:
            error_message = traceback.format_exc()
            queue.put((False, error_message))

    queue = multiprocessing.Queue()
    process = multiprocessing.Process(
        target=wrapper, args=(queue, *args), kwargs=kwargs
    )
    process.start()
    process.join(timeout)

    if process.is_alive():
        logger.error("Process timed out. Terminating process.")
        process.terminate()
        process.join()
        return False, "Process timed out."
    try:
        success, result = queue.get(timeout=1)
    except:
        return False, "error"
    if success:
        logger.info("Function executed successfully.")
        return True, result
    else:
        logger.error("Function failed with error:", result)
        return False, result


if __name__ == "__main__":
    source_file, target_file = (
        f"source.csv",
        f"result.csv",
    )
    logger.info(f"{source_file=}")
    while True:
        success, result = run_function_in_subprocess(
            get_abbrs_from_pmc, 1800, source_file, target_file
        )
        logger.info(f"{result=}")
        if success:
            break
