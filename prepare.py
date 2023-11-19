import os


def prepare():
    os.environ["HF_HOME"] = "/cs/snapless/gabis/gabis/shared/huggingface"
    os.environ["HF_DATASETS_CACHE"] = "/cs/snapless/gabis/gabis/shared/huggingface/datasets"
    os.environ["HF_METRICS_CACHE"] = "/cs/snapless/gabis/gabis/shared/huggingface/metrics"
    os.environ["HF_MODULES_CACHE"] = "/cs/snapless/gabis/gabis/shared/huggingface/modules"
    os.environ["HF_DATASETS_DOWNLOADED_EVALUATE_PATH"] = \
         "/cs/snapless/gabis/gabis/shared/huggingface/datasets_downloaded_evaluate"
    os.environ["TRANSFORMERS_CACHE"] = "/cs/snapless/gabis/gabis/shared/huggingface/models"
    os.environ["TORCH_HOME"] = "/cs/snapless/gabis/gabis/shared/torch_home"


if __name__ == "__main__":
    prepare()
