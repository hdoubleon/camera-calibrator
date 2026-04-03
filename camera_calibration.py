import cv2 as cv
import numpy as np


def select_img_from_video(video_file, board_pattern, select_all=False, wait_msec=10):
    # 동영상 파일 열기
    video = cv.VideoCapture(video_file)
    assert video.isOpened(), "Cannot read the given input, " + str(video_file)

    img_select = []
    print(
        "동영상이 재생됩니다. 체스보드가 잘 보이는 순간 '스페이스바'를 눌러 캡처하세요."
    )
    print("종료하려면 'ESC' 키를 누르세요.")

    while True:
        valid, img = video.read()
        if not valid:
            break

        if select_all:
            img_select.append(img)
        else:
            # 영상을 화면에 띄우고 키 입력 대기
            cv.imshow("Video", img)
            key = cv.waitKey(wait_msec)

            if key == 27:  # ESC 키: 영상 재생 종료
                break
            elif key == ord(" "):  # 스페이스바: 현재 프레임 캡처
                # 체스보드가 화면에 제대로 인식되는지 확인 후 리스트에 추가
                gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
                complete, pts = cv.findChessboardCorners(gray, board_pattern)
                if complete:
                    # 인식된 코너를 화면에 무지개색으로 그려서 잠깐 보여줌
                    cv.drawChessboardCorners(img, board_pattern, pts, complete)
                    cv.imshow("Video", img)
                    cv.waitKey(500)  # 0.5초 대기

                    img_select.append(img)
                    print(f"캡처 성공! 현재까지 모인 이미지: {len(img_select)}장")
                else:
                    print(
                        "체스보드를 찾을 수 없습니다. 다른 각도에서 다시 캡처해보세요."
                    )

    video.release()
    cv.destroyAllWindows()
    return img_select


def calib_camera_from_chessboard(
    images, board_pattern, board_cellsize, K=None, dist_coeff=None, calib_flags=None
):
    # 1. 2D 픽셀 좌표 찾기
    img_points = []
    for img in images:
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        complete, pts = cv.findChessboardCorners(gray, board_pattern)
        if complete:
            img_points.append(pts)

    assert len(img_points) > 0, "There is no set of complete chessboard points!"

    # 2. 현실의 3D 좌표 생성
    obj_pts = [
        [c, r, 0] for r in range(board_pattern[1]) for c in range(board_pattern[0])
    ]
    obj_points = [np.array(obj_pts, dtype=np.float32) * board_cellsize] * len(
        img_points
    )

    # 3. 캘리브레이션 함수 실행
    return cv.calibrateCamera(
        obj_points, img_points, gray.shape[::-1], K, dist_coeff, flags=calib_flags
    )


if __name__ == "__main__":
    # ==========================================
    # 1. 과제 환경에 맞게 변수 설정 (수정 필요!)
    # ==========================================
    video_file = "chessboard.MOV"  # 스마트폰이나 액션캠으로 찍은 영상 경로
    board_pattern = (13, 9)  # 체스보드 내부 코너 개수 (가로, 세로)
    board_cellsize = 0.020  # 인쇄한 체스보드 한 칸의 물리적 크기 (예: 2.5cm -> 0.025m)

    # 2. 동영상에서 캘리브레이션에 쓸 이미지 캡처
    images = select_img_from_video(video_file, board_pattern)

    # 3. 캡처된 이미지가 있으면 캘리브레이션 진행
    if len(images) > 0:
        print("\n수학적 최적화 계산 중... (수십 초 정도 걸릴 수 있습니다)")
        rms, K, dist_coeff, rvecs, tvecs = calib_camera_from_chessboard(
            images, board_pattern, board_cellsize
        )

        # 4. 과제 제출용 결과 출력
        print("\n====== [Camera Calibration Results] ======")
        print(f"* RMS error (rmse): {rms:.4f}")
        print(f"* Camera matrix (K):\n{K}")
        print(f"  - fx: {K[0,0]:.4f}")
        print(f"  - fy: {K[1,1]:.4f}")
        print(f"  - cx: {K[0,2]:.4f}")
        print(f"  - cy: {K[1,2]:.4f}")
        print(f"* Distortion coefficients: {dist_coeff.flatten()}")
        print("==========================================")
        print("위 결과값들을 복사해서 과제 저장소의 README.md 파일에 작성하세요!")
    else:
        print("캡처된 이미지가 없어 캘리브레이션을 수행할 수 없습니다.")
