from django.shortcuts import render, HttpResponse
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
import os
import cv2
import mediapipe as mp
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from .forms import VideoUploadForm


def index(request):
    return render(request, "index.html")


def trye(request):
    return render(request, "AI.html")


def Privacy_policy(request):
    return HttpResponse("Privacy Policy")


def soc(request):
    return render(request, "soc.html")


mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

EYE_AR_THRESH = 0.13
FRAME_HISTORY = 30
HEAD_ANGLE_THRESH = 25
LEFT_EYE = [362, 385, 387, 263, 373, 380]
RIGHT_EYE = [33, 160, 158, 133, 153, 144]


def eye_aspect_ratio(eye):
    vertical_dist = np.linalg.norm(eye[1] - eye[5]) + np.linalg.norm(eye[2] - eye[4])
    horizontal_dist = np.linalg.norm(eye[0] - eye[3])
    return vertical_dist / (2 * horizontal_dist)


def calculate_engagement(head_angle, eye_ar, eyes_closed):
    head_weight = 0.4
    eye_weight = 0.6
    head_score = max(0, min(1, 1 - abs(head_angle[0]) / HEAD_ANGLE_THRESH))
    eye_score = 0 if eyes_closed else min(1, eye_ar / EYE_AR_THRESH)
    return (head_score * head_weight) + (eye_score * eye_weight)


def ai_handler(request):
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Сохранение видео
            video_file = request.FILES['video_file']
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            video_filename = f'video_{timestamp}.mp4'
            video_path = os.path.join(settings.MEDIA_ROOT, 'uploads', video_filename)

            os.makedirs(os.path.dirname(video_path), exist_ok=True)

            with open(video_path, 'wb+') as destination:
                for chunk in video_file.chunks():
                    destination.write(chunk)

            # Обработка видео
            results = process_video(video_path)

            # Расчет всех метрик
            total_frames = results['total_frames']
            eyes_closed_percent = round(results['eyes_closed_frames'] / total_frames * 100, 2) if total_frames > 0 else 0
            head_distracted_percent = round(results['head_distracted_frames'] / total_frames * 100, 2) if total_frames > 0 else 0
            avg_engagement = round(np.mean(results['engagement_history']), 2) if results['engagement_history'] else 0
            max_engagement = round(np.max(results['engagement_history']), 2) if results['engagement_history'] else 0
            min_engagement = round(np.min(results['engagement_history']), 2) if results['engagement_history'] else 0

            # Генерация графика

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            plot_filename = f'engagement_{timestamp}.png'
            generate_engagement_plot(
                engagement_history=results['engagement_history'],
                fps=results['fps'],
                eyes_closed_frames=results['eyes_closed_frames'],
                head_distracted_frames=results['head_distracted_frames'],
                plt_f_n=plot_filename,

            )

            # Подготовка контекста
            context = {
                'video_url': os.path.join(settings.MEDIA_URL, 'uploads', video_filename),
                'plot_url': os.path.join(settings.MEDIA_URL, 'plots', plot_filename),
                'timestamp': timestamp,
                'metrics': {
                    'total_frames': total_frames,
                    'fps': results['fps'],
                    'duration': round(total_frames / results['fps'], 2) if results['fps'] > 0 else 0,
                    'engagement': {
                        'average': avg_engagement,
                        'average_percent': avg_engagement * 100,  # Предварительно умножаем на 100
                        'max': max_engagement,
                        'min': min_engagement,
                    },
                    'eyes_closed': {
                        'count': results['eyes_closed_frames'],
                        'percent': eyes_closed_percent,
                        'percent_value': eyes_closed_percent,  # Уже в процентах
                    },
                    'head_distracted': {
                        'count': results['head_distracted_frames'],
                        'percent': head_distracted_percent,
                        'percent_value': head_distracted_percent,  # Уже в процентах
                    }
                },
                'thresholds': {
                    'eye_aspect': 0.13,  # EYE_AR_THRESH
                    'head_angle': 25,  # HEAD_ANGLE_THRESH
                }
            }

            return render(request, 'ang_analz.html', context)

    return render(request, 'upload_file.html', {'form': VideoUploadForm()})


def process_video(video_path):
    """Process video file and return engagement metrics."""
    cap = cv2.VideoCapture(video_path)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    engagement_history = []
    eyes_closed_frames = 0
    head_distracted_frames = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_frame)
        engagement = 0

        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark

            # Head direction analysis
            image_points = np.array([
                (landmarks[1].x, landmarks[1].y),
                (landmarks[33].x, landmarks[33].y),
                (landmarks[263].x, landmarks[263].y)
            ], dtype="float32")

            nose_position = image_points[0]
            head_offset = np.array([0.5, 0.5]) - nose_position
            head_angle = head_offset * [180, 90]

            # Eye analysis
            left_eye = np.array([(landmarks[i].x, landmarks[i].y) for i in LEFT_EYE])
            right_eye = np.array([(landmarks[i].x, landmarks[i].y) for i in RIGHT_EYE])
            ear = (eye_aspect_ratio(left_eye) + eye_aspect_ratio(right_eye)) / 2

            eyes_closed = ear < EYE_AR_THRESH
            engagement = calculate_engagement(head_angle, ear, eyes_closed)

            # Update counters
            eyes_closed_frames += 1 if eyes_closed else 0
            head_distracted = np.linalg.norm(head_angle) > HEAD_ANGLE_THRESH
            head_distracted_frames += 1 if head_distracted else 0

        engagement_history.append(engagement)

    cap.release()

    return {
        'engagement_history': engagement_history,
        'fps': fps,
        'eyes_closed_frames': eyes_closed_frames,
        'head_distracted_frames': head_distracted_frames,
        'total_frames': len(engagement_history)
    }

def generate_engagement_plot(engagement_history, fps, eyes_closed_frames, head_distracted_frames,plt_f_n):
    """Generate and save engagement plot."""
    plot_path = os.path.join(settings.MEDIA_ROOT, 'plots', plt_f_n)
    time_axis = np.arange(len(engagement_history)) / fps

    plt.figure(figsize=(14, 7))
    plt.plot(time_axis, engagement_history, color='blue', linestyle='--', linewidth=1, alpha=0.3, label='Raw Data')

    smoothed = np.convolve(engagement_history, np.ones(FRAME_HISTORY) / FRAME_HISTORY, mode='same')
    plt.plot(time_axis, smoothed, color='red', linestyle='-', linewidth=2, label='Smoothed Engagement')
    plt.fill_between(time_axis, smoothed, color='red', alpha=0.2)

    plt.axhline(y=0.5, color='gray', linestyle='--', linewidth=1, label='50% Threshold')
    plt.axhline(y=0.8, color='orange', linestyle='--', linewidth=1, label='80% Threshold')

    if eyes_closed_frames > 0:
        plt.annotate('Eyes Closed', xy=(time_axis[np.argmin(engagement_history)], np.min(engagement_history)),
                     xytext=(10, 30), textcoords='offset points', arrowprops=dict(arrowstyle='->'))
    if head_distracted_frames > 0:
        plt.annotate('Head Distracted', xy=(time_axis[np.argmin(engagement_history)], np.min(engagement_history)),
                     xytext=(10, 50), textcoords='offset points', arrowprops=dict(arrowstyle='->'))

    plt.title('Engagement Analysis Over Time', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Time (seconds)', fontsize=12)
    plt.ylabel('Engagement Level', fontsize=12)
    plt.legend(loc='upper right', fontsize=10)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.ylim(0, 1)

    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close()

    return plot_path
# def generate_engagement_plot(engagement_history, fps, eyes_closed_frames, head_distracted_frames, plot_path):
#     """Генерация и сохранение графика вовлечённости"""
#     plt.figure(figsize=(14, 7))
#
#     # Ось времени (секунды)
#     time_axis = np.arange(len(engagement_history)) / fps
#
#     # Сырые данные
#     plt.plot(time_axis, engagement_history, color='blue', linestyle='--',
#              linewidth=1, alpha=0.3, label='Сырые данные')
#
#     # Сглаженные данные
#     smoothed = np.convolve(engagement_history, np.ones(30) / 30, mode='same')
#     plt.plot(time_axis, smoothed, color='red', linewidth=2,
#              label='Сглаженная вовлечённость')
#
#     # Пороговые линии
#     plt.axhline(y=0.5, color='gray', linestyle='--', label='Порог 50%')
#     plt.axhline(y=0.8, color='green', linestyle='--', label='Порог 80%')
#
#     # Аннотации
#     if eyes_closed_frames > 0:
#         plt.annotate('Глаза закрыты',
#                      xy=(time_axis[np.argmin(engagement_history)], np.min(engagement_history)),
#                      xytext=(10, 30),
#                      arrowprops=dict(arrowstyle='->'))
#
#     if head_distracted_frames > 0:
#         plt.annotate('Отвлечение',
#                      xy=(time_axis[np.argmin(engagement_history)], np.min(engagement_history)),
#                      xytext=(10, 50),
#                      arrowprops=dict(arrowstyle='->'))
#
#     # Оформление
#     plt.title('Динамика вовлечённости', fontsize=16)
#     plt.xlabel('Время (секунды)', fontsize=12)
#     plt.ylabel('Уровень вовлечённости', fontsize=12)
#     plt.legend()
#     plt.grid(True)
#     plt.ylim(0, 1)
#
#     # Сохранение
#     plt.savefig(plot_path, dpi=300, bbox_inches='tight')
#     plt.close()


