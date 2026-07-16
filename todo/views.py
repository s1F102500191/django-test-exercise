import random

from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.views.decorators.http import require_POST

from todo.models import Task

RANDOM_TASK_TITLES = [
    '宇宙人に会う準備をする',
    '冷蔵庫と会話する',
    'ネコの通訳になる',
    'タイムマシンの修理を依頼する',
    '空飛ぶバナナを探す',
    '透明人間に手紙を書く',
    '月面で筋トレする',
    '未確認生物に名刺を渡す',
    '巨大なカレーライスを描く',
    '机に住む妖精を探す',
    '魔法の鉛筆で絵を描く',
    '踊る冷蔵庫を止める',
    '猫耳付き傘を編む',
    '未来の自分にメールを送る',
    '空気と格闘する',
    'ビルのてっぺんで昼寝する',
    '幽霊に朝ごはんを作る',
    '虹の端を掃除する',
    '呼吸するたびに点数をつける',
    'テレビと相談して予定を決める',
    '不思議な箱を開けないで閉じる',
    '逆さまに歩いてみる',
    '電車の駅に魚を連れて行く',
    'カバンの中を海にする',
    'スプーンで星をすくう',
    '雨雲に謝る',
    '夢の中で散歩する',
    '砂糖と塩を交換する',
    '時計の針を追いかける',
    '世界一高いケーキを設計する',
    'トースターと相談して朝食を決める',
    '土星の輪を掃除する',
    '椅子とチェスをする',
    '電話をかけずに電話をかける',
    'おばけと一緒にラジオ体操',
    '夢の中の郵便局に手紙を出す',
    '雲の形を分類する',
    '歌う鉛筆を見つける',
    '電車の窓に絵を描く',
    '砂漠でアイスクリームを売る',
    'ペンギンにパソコンを教える',
    '図書館で透明な本を読む',
    '左足だけでダンスをする',
    '鏡の中の自分に手紙を書く',
    '風船で部屋を飛ばす',
    '鍵を忘れた家に招待される',
    'スマホに逆さまに話しかける',
    '植木鉢の中の森を散歩する',
    '冷蔵庫の中で演説をする',
    'チョコレートの雨を予測する',
    '月とキャッチボールをする',
    '幽霊の友だちに花を贈る',
    '自転車を逆さまに乗る',
    '影に向かって挨拶する',
    '洗濯機と握手する',
    '風船を作って空を飛ぶ',
    'おばけの英語を勉強する',
    '帽子と踊る',
    '時計に名前をつける',
    '紙飛行機で手紙を送る',
    'キャンディーを料理する',
    '星と読書会を開く',
    'オーブンに絵を描く',
    'ペットボトルに手紙を入れる',
    '鏡に質問をする',
    '砂の城を高く積む',
    '消しゴムを釣りに使う',
    'スマホで歌を録音する',
    '金魚に話しかける',
    '朝食を逆さまに食べる',
    '象に傘を貸す',
    'こたつでスケッチをする',
    'ラジオにサインを送る',
    'トマトと会議を開く',
    '空の駅で待ち合わせする',
    '鏡の中で道案内をする',
    'カーテンに秘密をつたえる',
    '消しゴムの歌を作る',
    '猫の夢を記録する',
    '木の葉でカレンダーを作る',
    'カップ麺を宇宙服で食べる',
    '新聞紙で帽子を折る',
    '竹の中に手紙を隠す',
    'バナナで橋を渡る',
    '夜空にアイスクリームを飛ばす',
    '光る石を集める',
    '鳥に乗って買い物に行く',
    'トランポリンで電話する',
    '壁に向かって歌う',
    '朝の光を料理する',
    'スイカでかばんを作る',
    '影の傘をさす',
    '靴下を宇宙に送る',
    '雲のかけらを集める',
    '星の数を数える',
    '空っぽの箱に夢を詰める',
    '机の上でピクニックをする',
    '雲に手紙をかく',
    '飴玉で地図を描く',
    '電気をほめる',
    '絵筆で音楽を描く',
    'バス停に花を植える',
    '氷でダンスをする',
    '魚のために本を読む',
    'スープに星を浮かべる',
    '背中に地図を描く',
    '流れ星に願いを伝える',
]


def parse_due_at(value):
    if not value:
        return None

    due_at = parse_datetime(value)

    if due_at is None:
        return None

    if timezone.is_naive(due_at):
        due_at = timezone.make_aware(due_at)

    return due_at


def index(request):
    if request.method == 'POST':
        priority = request.POST.get('priority', 'normal')

        # random アクションが指定されていればランダムなタイトルを採用
        if request.POST.get('action') == 'random':
            title = random.choice(RANDOM_TASK_TITLES)
            due_at = None
        else:
            title = request.POST.get('title', '').strip()
            # もし入力タイトルが空ならデフォルトを割り当て
            if not title:
                title = "ランダムなタスク"
            due_at = parse_due_at(request.POST.get('due_at'))

        Task.objects.create(
            title=title,
            due_at=due_at,
            priority=priority  # 優先度の追加
        )

        return redirect('index')

    if request.GET.get('order') == 'due':
        tasks = Task.objects.order_by('due_at')
    else:
        tasks = Task.objects.order_by('-posted_at')

    context = {
        'tasks': tasks
    }
    return render(request, 'todo/index.html', context)

def detail(request, task_id):
    task = get_object_or_404(Task, pk=task_id)

    context = {
        'task': task
    }
    return render(request, 'todo/detail.html', context)


def update(request, task_id):
    task = get_object_or_404(Task, pk=task_id)

    if request.method == 'POST':
        task.title = request.POST.get('title', '').strip()
        task.due_at = parse_due_at(request.POST.get('due_at'))
        task.priority = request.POST.get('priority', 'normal')  # 優先度を更新
        task.save()

        return redirect('detail', task_id=task.id)

    context = {
        'task': task
    }
    return render(request, 'todo/edit.html', context)


@require_POST
def close(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    task.completed = True
    task.save()

    return redirect('index')


@require_POST
def delete(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    task.delete()

    return redirect('index')