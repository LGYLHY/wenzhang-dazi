"""统一错误信封：{code, message}"""
from fastapi import HTTPException


class BizError(HTTPException):
    """业务异常，code 给前端做分支判断，message 给用户看"""

    def __init__(self, code: str, message: str, http_status: int = 400):
        super().__init__(status_code=http_status, detail={"code": code, "message": message})


# 错误码集中管理
CODE_EMPTY_INPUT = "EMPTY_INPUT"            # 未输入图片或文字
CODE_INVALID_IMG = "INVALID_IMAGE"          # 格式 / 大小不符
CODE_RECOG_FAIL = "RECOGNITION_FAILED"      # 多模态识别失败
CODE_MODEL_TIMEOUT = "MODEL_TIMEOUT"        # 生成超时
CODE_NETWORK = "NETWORK_ERROR"              # 网络中断
CODE_RATE_LIMIT = "RATE_LIMIT"              # 限流
CODE_INTERNAL = "INTERNAL"                  # 兜底
