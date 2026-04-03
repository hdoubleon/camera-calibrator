import cv2 as cv
import numpy as np

# ==========================================
# 1. 캘리브레이션 결과 입력 (camera_calibration.py에서 얻은 값으로 수정 필수!)
# ==========================================
video_file = "chessboard.MOV"  # 왜곡을 보정할 원본 동영상 파일 경로

# 새로 구한 더욱 정교해진 카메라 스펙!
K = np.array([[887.6764, 0, 956.5140], [0, 884.6162, 531.5657], [0, 0, 1]])

# p1, p2, k3를 0으로 강제 초기화하여 오버피팅 방지
dist_coeff = np.array([-0.01492128, 0.1062357, 0.0, 0.0, 0.0])

# ==========================================
# 2. 동영상 열기 및 초기 설정
# ==========================================
video = cv.VideoCapture(video_file)
assert video.isOpened(), "Cannot read the given input, " + str(video_file)

show_rectify = True  # True면 보정된 화면, False면 원본 화면
map1, map2 = None, None

print("영상이 재생됩니다.")
print("  - [스페이스바]: 원본(Original) / 보정(Rectified) 화면 전환 (토글)")
print("  - [ESC]: 재생 종료")

# ⭐ 창 이름 분열을 막기 위해 변수로 하나로 통일!
window_name = "Lens Distortion Correction"

# ==========================================
# 3. 프레임별 왜곡 보정 루프
# ==========================================
while True:
    valid, img = video.read()
    if not valid:
        break  # 영상이 끝나면 루프 탈출

    if show_rectify:
        if map1 is None or map2 is None:
            map1, map2 = cv.initUndistortRectifyMap(
                K, dist_coeff, None, None, (img.shape[1], img.shape[0]), cv.CV_32FC1
            )

        # 보정된 이미지 생성
        rectified_img = cv.remap(img, map1, map2, interpolation=cv.INTER_LINEAR)

        # 원본과 보정본에 각각 글자 쓰기
        cv.putText(
            img, "Original", (10, 30), cv.FONT_HERSHEY_DUPLEX, 1.0, (0, 0, 255), 2
        )
        cv.putText(
            rectified_img,
            "Rectified",
            (10, 30),
            cv.FONT_HERSHEY_DUPLEX,
            1.0,
            (0, 255, 0),
            2,
        )

        # 두 이미지를 가로로 나란히 이어 붙이기
        combined_img = np.hstack((img, rectified_img))

        # ⭐ 통일된 창 이름 사용
        cv.imshow(window_name, combined_img)

    else:
        # 스페이스바를 눌러 show_rectify가 False일 때는 원본만 띄우기
        cv.putText(
            img, "Original Only", (10, 30), cv.FONT_HERSHEY_DUPLEX, 1.0, (0, 0, 255), 2
        )

        # ⭐ 통일된 창 이름 사용
        cv.imshow(window_name, img)

    # 키보드 입력 처리 (약 30ms 대기 - 영상 재생 속도 조절)
    key = cv.waitKey(30)
    if key == 27:  # ESC 키
        break
    elif key == ord(" "):  # 스페이스바
        show_rectify = not show_rectify  # True/False 상태 뒤집기 (토글)

video.release()
cv.destroyAllWindows()
