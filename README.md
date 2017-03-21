# Python-PixivCrawler
爬取Pixiv日榜前10的图片（包括Gif）
>由于P站的Gif并没有直接的图片资源，而是以压缩包的形式储存Gif的每一帧，该代码实际上是下载其压缩包解压再将每一帧合成一个Gif

>Gif合帧部分参考http://blog.csdn.net/yangalbert/article/details/7603338

>注：该合成Gif部分还是有瑕疵。另该代码是单线程，并且无重新请求。
