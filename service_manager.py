"""
서비스 매니저: ComfyUI와 Stable Diffusion WebUI를 자동으로 시작/관리하는 통합 시스템
"""
import os
import sys
import subprocess
import time
import requests
import signal
import logging
from pathlib import Path
from typing import Optional, Dict
from threading import Thread
try:
    import psutil
except ImportError:
    psutil = None

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ServiceManager:
    """ComfyUI와 Stable Diffusion WebUI 서비스를 관리하는 클래스"""
    
    def __init__(
        self,
        comfyui_path: Optional[str] = None,
        webui_path: Optional[str] = None,
        comfyui_port: Optional[int] = None,
        webui_port: Optional[int] = None,
        auto_start: Optional[bool] = None,
        health_check_interval: Optional[int] = None
    ):
        """
        Args:
            comfyui_path: ComfyUI 디렉토리 경로 (None이면 config에서 로드)
            webui_path: Stable Diffusion WebUI 디렉토리 경로 (None이면 config에서 로드)
            comfyui_port: ComfyUI 서버 포트 (None이면 config에서 로드)
            webui_port: WebUI 서버 포트 (None이면 config에서 로드)
            auto_start: 시작 시 자동으로 서비스 시작 여부 (None이면 config에서 로드)
            health_check_interval: 헬스체크 간격 (초) (None이면 config에서 로드)
        """
        # config 모듈에서 설정 로드 (새 구조 우선, 레거시 fallback)
        try:
            from app.core.config import (
                COMFYUI_PATH, WEBUI_PATH, COMFYUI_PORT, WEBUI_PORT,
                AUTO_START_SERVICES, HEALTH_CHECK_INTERVAL, PROJECT_ROOT
            )
            PROJECT_ROOT = Path(PROJECT_ROOT)
        except ImportError:
            # 레거시 config fallback
            try:
                from config import (
                    COMFYUI_PATH, WEBUI_PATH, COMFYUI_PORT, WEBUI_PORT,
                    AUTO_START_SERVICES, HEALTH_CHECK_INTERVAL
                )
                PROJECT_ROOT = Path(__file__).parent.absolute()
            except ImportError:
                # 기본값 사용
                COMFYUI_PATH = None
                WEBUI_PATH = None
                COMFYUI_PORT = 8188
                WEBUI_PORT = 7860
                AUTO_START_SERVICES = True
                HEALTH_CHECK_INTERVAL = 10
                PROJECT_ROOT = Path(__file__).parent.absolute()
        
        self.project_root = PROJECT_ROOT
        
        # 경로 설정 (인자 우선, 없으면 config, 없으면 None)
        if comfyui_path:
            self.comfyui_path = Path(comfyui_path)
        elif COMFYUI_PATH:
            self.comfyui_path = Path(COMFYUI_PATH)
        else:
            self.comfyui_path = None
        
        if webui_path:
            self.webui_path = Path(webui_path)
        elif WEBUI_PATH:
            self.webui_path = Path(WEBUI_PATH)
        else:
            self.webui_path = None
        
        self.comfyui_port = comfyui_port if comfyui_port is not None else COMFYUI_PORT
        self.webui_port = webui_port if webui_port is not None else WEBUI_PORT
        self.auto_start = auto_start if auto_start is not None else AUTO_START_SERVICES
        self.health_check_interval = health_check_interval if health_check_interval is not None else HEALTH_CHECK_INTERVAL
        
        # 프로세스 관리
        self.comfyui_process: Optional[subprocess.Popen] = None
        self.webui_process: Optional[subprocess.Popen] = None
        
        # 헬스체크
        self.health_check_thread: Optional[Thread] = None
        self.running = False
        
        # health_check_interval이 None이면 기본값 설정
        if self.health_check_interval is None:
            self.health_check_interval = 10
        
        # 환경 변수 설정
        self._setup_environment()
        
        logger.info(f"ServiceManager 초기화 완료")
        logger.info(f"  ComfyUI 경로: {self.comfyui_path}")
        logger.info(f"  WebUI 경로: {self.webui_path}")
    
    def _setup_environment(self):
        """환경 변수 설정"""
        # Python 경로 설정 (가상환경 우선)
        venv_python = self.project_root / "venv" / "bin" / "python"
        if venv_python.exists():
            self.python_executable = str(venv_python)
        else:
            self.python_executable = sys.executable
        
        # ComfyUI 가상환경 확인
        comfyui_venv = self.comfyui_path / "venv" / "bin" / "python"
        if comfyui_venv.exists():
            self.comfyui_python = str(comfyui_venv)
        else:
            self.comfyui_python = self.python_executable
        
        # WebUI 가상환경 확인
        webui_venv = self.webui_path / "venv" / "bin" / "python"
        if webui_venv.exists():
            self.webui_python = str(webui_venv)
        else:
            self.webui_python = self.python_executable
    
    def _check_service_health(self, url: str, timeout: int = 5) -> bool:
        """서비스 헬스체크"""
        try:
            response = requests.get(url, timeout=timeout, allow_redirects=True)
            # 200-299 범위의 상태 코드를 성공으로 간주
            return 200 <= response.status_code < 300
        except requests.exceptions.RequestException as e:
            logger.debug(f"헬스체크 실패 ({url}): {e}")
            return False
        except Exception as e:
            logger.debug(f"헬스체크 예외 ({url}): {e}")
            return False
    
    def start_comfyui(self) -> bool:
        """ComfyUI 서버 시작"""
        if self.comfyui_process and self.comfyui_process.poll() is None:
            logger.info("ComfyUI가 이미 실행 중입니다")
            return True
        
        if not self.comfyui_path:
            logger.error("ComfyUI 경로가 설정되지 않았습니다. 환경 변수 COMFYUI_PATH를 설정하세요.")
            return False
        
        if not self.comfyui_path.exists():
            logger.error(f"ComfyUI 경로를 찾을 수 없습니다: {self.comfyui_path}")
            return False
        
        main_py = self.comfyui_path / "main.py"
        if not main_py.exists():
            logger.error(f"ComfyUI main.py를 찾을 수 없습니다: {main_py}")
            return False
        
        try:
            logger.info(f"ComfyUI 시작 중... (포트: {self.comfyui_port})")
            
            # ComfyUI 시작 (백그라운드)
            env = os.environ.copy()
            env['PYTHONUNBUFFERED'] = '1'
            # BrokenPipeError 방지를 위한 환경 변수
            env['PYTHONIOENCODING'] = 'utf-8'
            
            # 로그 파일 경로 설정
            log_dir = self.project_root / "logs"
            log_dir.mkdir(exist_ok=True)
            comfyui_log = log_dir / "comfyui.log"
            
            # stdout/stderr를 파일로 리다이렉트 (파이프 버퍼 문제 방지)
            log_file = open(comfyui_log, "a")
            self.comfyui_process = subprocess.Popen(
                [self.comfyui_python, str(main_py), "--port", str(self.comfyui_port)],
                cwd=str(self.comfyui_path),
                env=env,
                stdout=log_file,
                stderr=subprocess.STDOUT,  # stderr도 같은 파일로
                start_new_session=True  # macOS에서 os.setsid 대신 사용
            )
            # 파일 핸들은 프로세스가 종료될 때까지 열어둠
            
            # 서버가 시작될 때까지 대기
            max_wait = 60  # 최대 60초 대기
            wait_time = 0
            while wait_time < max_wait:
                if self._check_service_health(f"http://127.0.0.1:{self.comfyui_port}"):
                    logger.info(f"✅ ComfyUI가 성공적으로 시작되었습니다 (포트: {self.comfyui_port})")
                    return True
                if self.comfyui_process.poll() is not None:
                    # 프로세스가 종료됨
                    comfyui_log = self.project_root / "logs" / "comfyui.log"
                    if comfyui_log.exists():
                        # 로그 파일의 마지막 몇 줄 읽기
                        try:
                            with open(comfyui_log, "r") as f:
                                lines = f.readlines()
                                error_msg = "".join(lines[-20:])  # 마지막 20줄
                                logger.error(f"ComfyUI 시작 실패. 로그:\n{error_msg}")
                        except Exception as e:
                            logger.error(f"ComfyUI 시작 실패 (로그 읽기 오류: {e})")
                    else:
                        logger.error("ComfyUI 프로세스가 예상치 못하게 종료되었습니다")
                    return False
                time.sleep(1)
                wait_time += 1
            
            logger.warning(f"ComfyUI 시작 확인 시간 초과 (포트: {self.comfyui_port})")
            return False
            
        except Exception as e:
            logger.error(f"ComfyUI 시작 중 오류 발생: {e}")
            return False
    
    def start_webui(self) -> bool:
        """Stable Diffusion WebUI 서버 시작"""
        if self.webui_process and self.webui_process.poll() is None:
            logger.info("WebUI가 이미 실행 중입니다")
            return True
        
        if not self.webui_path:
            logger.error("WebUI 경로가 설정되지 않았습니다. 환경 변수 WEBUI_PATH를 설정하세요.")
            return False
        
        if not self.webui_path.exists():
            logger.error(f"WebUI 경로를 찾을 수 없습니다: {self.webui_path}")
            return False
        
        webui_py = self.webui_path / "webui.py"
        if not webui_py.exists():
            logger.error(f"WebUI webui.py를 찾을 수 없습니다: {webui_py}")
            return False
        
        try:
            logger.info(f"Stable Diffusion WebUI 시작 중... (포트: {self.webui_port})")
            
            # WebUI 시작 (백그라운드, API만 모드)
            env = os.environ.copy()
            env['PYTHONUNBUFFERED'] = '1'
            
            # 로그 파일 경로 설정
            log_dir = self.project_root / "logs"
            log_dir.mkdir(exist_ok=True)
            webui_log = log_dir / "webui.log"
            
            # stdout/stderr를 파일로 리다이렉트 (파이프 버퍼 문제 방지)
            log_file = open(webui_log, "a")
            self.webui_process = subprocess.Popen(
                [self.webui_python, str(webui_py), "--api", "--port", str(self.webui_port)],
                cwd=str(self.webui_path),
                env=env,
                stdout=log_file,
                stderr=subprocess.STDOUT,  # stderr도 같은 파일로
                start_new_session=True  # macOS에서 os.setsid 대신 사용
            )
            # 파일 핸들은 프로세스가 종료될 때까지 열어둠
            
            # 서버가 시작될 때까지 대기
            max_wait = 120  # WebUI는 더 오래 걸릴 수 있음
            wait_time = 0
            while wait_time < max_wait:
                if self._check_service_health(f"http://127.0.0.1:{self.webui_port}"):
                    logger.info(f"✅ Stable Diffusion WebUI가 성공적으로 시작되었습니다 (포트: {self.webui_port})")
                    return True
                if self.webui_process.poll() is not None:
                    # 프로세스가 종료됨
                    webui_log = self.project_root / "logs" / "webui.log"
                    if webui_log.exists():
                        # 로그 파일의 마지막 몇 줄 읽기
                        try:
                            with open(webui_log, "r") as f:
                                lines = f.readlines()
                                error_msg = "".join(lines[-20:])  # 마지막 20줄
                                logger.error(f"WebUI 시작 실패. 로그:\n{error_msg}")
                        except Exception as e:
                            logger.error(f"WebUI 시작 실패 (로그 읽기 오류: {e})")
                    else:
                        logger.error("WebUI 프로세스가 예상치 못하게 종료되었습니다")
                    return False
                time.sleep(2)
                wait_time += 2
            
            logger.warning(f"WebUI 시작 확인 시간 초과 (포트: {self.webui_port})")
            return False
            
        except Exception as e:
            logger.error(f"WebUI 시작 중 오류 발생: {e}")
            return False
    
    def stop_comfyui(self):
        """ComfyUI 서버 중지"""
        if self.comfyui_process:
            try:
                # 프로세스가 실제로 실행 중인지 확인
                if self.comfyui_process.poll() is None:
                    # 프로세스가 실행 중
                    if sys.platform == 'win32':
                        self.comfyui_process.terminate()
                    else:
                        # start_new_session=True를 사용했으므로 직접 프로세스에 신호 전송
                        try:
                            os.killpg(os.getpgid(self.comfyui_process.pid), signal.SIGTERM)
                        except (ProcessLookupError, OSError):
                            # 프로세스 그룹이 없으면 직접 종료
                            self.comfyui_process.terminate()
                    
                    # 프로세스 종료 대기
                    try:
                        self.comfyui_process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        logger.warning("ComfyUI 강제 종료 중...")
                        if sys.platform == 'win32':
                            self.comfyui_process.kill()
                        else:
                            try:
                                os.killpg(os.getpgid(self.comfyui_process.pid), signal.SIGKILL)
                            except (ProcessLookupError, OSError):
                                self.comfyui_process.kill()
                        self.comfyui_process.wait()
                    
                    logger.info("ComfyUI가 중지되었습니다")
                else:
                    # 이미 종료됨
                    logger.debug("ComfyUI 프로세스가 이미 종료되었습니다")
            except ProcessLookupError:
                # 프로세스가 이미 종료됨
                logger.debug("ComfyUI 프로세스가 이미 종료되었습니다")
            except Exception as e:
                logger.error(f"ComfyUI 중지 중 오류: {e}")
            finally:
                self.comfyui_process = None
    
    def stop_webui(self):
        """Stable Diffusion WebUI 서버 중지"""
        if self.webui_process:
            try:
                # 프로세스가 실제로 실행 중인지 확인
                if self.webui_process.poll() is None:
                    # 프로세스가 실행 중
                    if sys.platform == 'win32':
                        self.webui_process.terminate()
                    else:
                        # start_new_session=True를 사용했으므로 직접 프로세스에 신호 전송
                        try:
                            os.killpg(os.getpgid(self.webui_process.pid), signal.SIGTERM)
                        except (ProcessLookupError, OSError):
                            # 프로세스 그룹이 없으면 직접 종료
                            self.webui_process.terminate()
                    
                    # 프로세스 종료 대기
                    try:
                        self.webui_process.wait(timeout=15)
                    except subprocess.TimeoutExpired:
                        logger.warning("WebUI 강제 종료 중...")
                        if sys.platform == 'win32':
                            self.webui_process.kill()
                        else:
                            try:
                                os.killpg(os.getpgid(self.webui_process.pid), signal.SIGKILL)
                            except (ProcessLookupError, OSError):
                                self.webui_process.kill()
                        self.webui_process.wait()
                    
                    logger.info("Stable Diffusion WebUI가 중지되었습니다")
                else:
                    # 이미 종료됨
                    logger.debug("WebUI 프로세스가 이미 종료되었습니다")
            except ProcessLookupError:
                # 프로세스가 이미 종료됨
                logger.debug("WebUI 프로세스가 이미 종료되었습니다")
            except Exception as e:
                logger.error(f"WebUI 중지 중 오류: {e}")
            finally:
                self.webui_process = None
    
    def start_all(self) -> Dict[str, bool]:
        """모든 서비스 시작"""
        results = {
            "comfyui": self.start_comfyui(),
            "webui": False  # WebUI는 선택사항
        }
        
        # WebUI 시작 시도 (실패해도 계속 진행)
        try:
            results["webui"] = self.start_webui()
        except Exception as e:
            logger.warning(f"WebUI 시작 중 오류 (무시됨): {e}")
            results["webui"] = False
        
        return results
    
    def stop_all(self):
        """모든 서비스 중지"""
        self.stop_comfyui()
        self.stop_webui()
    
    def get_status(self) -> Dict[str, any]:
        """서비스 상태 조회"""
        comfyui_running = (
            self.comfyui_process is not None 
            and self.comfyui_process.poll() is None
            and self._check_service_health(f"http://127.0.0.1:{self.comfyui_port}")
        )
        
        webui_running = (
            self.webui_process is not None 
            and self.webui_process.poll() is None
            and self._check_service_health(f"http://127.0.0.1:{self.webui_port}")
        )
        
        return {
            "comfyui": {
                "running": comfyui_running,
                "port": self.comfyui_port,
                "url": f"http://127.0.0.1:{self.comfyui_port}"
            },
            "webui": {
                "running": webui_running,
                "port": self.webui_port,
                "url": f"http://127.0.0.1:{self.webui_port}"
            }
        }
    
    def _health_check_loop(self):
        """헬스체크 루프 (백그라운드 스레드)"""
        while self.running:
            try:
                status = self.get_status()
                
                # ComfyUI 자동 재시작 (프로세스가 실행 중이지만 응답하지 않는 경우만)
                if not status["comfyui"]["running"] and self.auto_start:
                    # 프로세스가 실행 중인지 확인
                    process_running = (
                        self.comfyui_process is not None 
                        and self.comfyui_process.poll() is None
                    )
                    
                    if process_running:
                        # 프로세스는 실행 중이지만 응답하지 않음 - 재시작
                        logger.warning("ComfyUI가 응답하지 않습니다. 재시작 시도...")
                        self.stop_comfyui()
                        time.sleep(3)  # 재시작 전 대기 시간 증가
                        self.start_comfyui()
                    elif self.comfyui_process is None:
                        # 프로세스가 없음 - 시작
                        logger.info("ComfyUI가 실행되지 않았습니다. 시작 시도...")
                        self.start_comfyui()
                
                # WebUI 자동 재시작 (프로세스가 실행 중이지만 응답하지 않는 경우만)
                if not status["webui"]["running"] and self.auto_start:
                    # 프로세스가 실행 중인지 확인
                    process_running = (
                        self.webui_process is not None 
                        and self.webui_process.poll() is None
                    )
                    
                    if process_running:
                        # 프로세스는 실행 중이지만 응답하지 않음 - 재시작
                        logger.warning("WebUI가 응답하지 않습니다. 재시작 시도...")
                        self.stop_webui()
                        time.sleep(3)  # 재시작 전 대기 시간 증가
                        self.start_webui()
                    elif self.webui_process is None:
                        # 프로세스가 없음 - 시작 (WebUI는 선택사항이므로 경고만)
                        logger.debug("WebUI가 실행되지 않았습니다.")
                
            except Exception as e:
                logger.error(f"헬스체크 중 오류: {e}")
            
            time.sleep(self.health_check_interval)
    
    def start_health_check(self):
        """헬스체크 시작"""
        if not self.running:
            self.running = True
            self.health_check_thread = Thread(target=self._health_check_loop, daemon=True)
            self.health_check_thread.start()
            logger.info("헬스체크가 시작되었습니다")
    
    def stop_health_check(self):
        """헬스체크 중지"""
        self.running = False
        if self.health_check_thread:
            self.health_check_thread.join(timeout=5)
        logger.info("헬스체크가 중지되었습니다")
    
    def __enter__(self):
        """컨텍스트 매니저 진입"""
        self.start_all()
        self.start_health_check()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """컨텍스트 매니저 종료"""
        self.stop_health_check()
        self.stop_all()


# 전역 서비스 매니저 인스턴스
_service_manager: Optional[ServiceManager] = None


def get_service_manager(**kwargs) -> ServiceManager:
    """전역 서비스 매니저 인스턴스 반환 (싱글톤)"""
    global _service_manager
    if _service_manager is None:
        _service_manager = ServiceManager(**kwargs)
    return _service_manager


if __name__ == "__main__":
    # 테스트 실행
    import sys
    
    print("서비스 매니저 테스트 시작...")
    
    with ServiceManager(auto_start=True) as manager:
        print("\n서비스 상태:")
        status = manager.get_status()
        for service, info in status.items():
            print(f"  {service}: {'✅ 실행 중' if info['running'] else '❌ 중지됨'} - {info['url']}")
        
        print("\n서비스가 실행 중입니다. 종료하려면 Ctrl+C를 누르세요...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n서비스 종료 중...")

