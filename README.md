## 一个简易的视频帧搜索工具

> source of idea: IIInoki(Twitter)

## How

把视频流用 ffmpeg 按照 packet 切分，然后视频递给 clip、音频递给 whisper 转成文字 text，再把这些文字内容生成 embedding 作为视频 packet 的附加 data 和原视频流 encode 到一起

## Usage

### Local

```bash
git clone video_embedding
python3 run.py --input x.mp4
```

### Docker

#### build

```bash
git clone video_embedding
cd video_embedding
docker build -t video_embedding:1.0 .
```

#### run

```bash
docker run -it \
-v /video:/space/ \
video_embedding:1.0 \
python3 run.py --input /space/x.mp4
```
