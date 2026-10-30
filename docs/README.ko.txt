Claude 사용량 트레이 - 설명서 (한국어)
=======================================
claude.ai(Pro / Max) 사용량과 남은 양을 언제든 보여 주고, 한도가 가까워지면 알려 주는
Windows 11 시스템 트레이 프로그램입니다.

빠른 시작
---------
1. 압축 파일을 원하는 위치에 풉니다.
2. START_HERE_Install.bat 을 더블클릭합니다 (언어는 자동으로 선택됩니다).
   "Windows의 PC 보호" 창이 뜨면 "추가 정보" → "실행"을 누르세요.
3. 작은 창이 나타나고 시스템 트레이(오른쪽 아래, ^ 안에 숨어 있으면 끌어내어 고정)에
   아이콘이 추가됩니다.
4. 처음 한 번만 브라우저 확장 프로그램을 설치합니다. 설치 프로그램이 기본 브라우저를
   감지해 확장 프로그램 페이지를 열고 폴더 경로를 클립보드에 복사합니다.
   검은 창에 표시되는 3단계를 따라 하세요 (아래 "브라우저별" 참고).
5. 그 브라우저에서 claude.ai 에 로그인하면 1분 안에 숫자가 나타납니다.

작동 방식
---------
claude.ai 에는 공개된 사용량 API 가 없습니다. 확장 프로그램은 "설정 > 사용량" 페이지에
표시된 숫자만 읽고(비밀번호와 쿠키는 건드리지 않음) 이 PC 안(http://127.0.0.1:47821)으로만
보냅니다. "내가 직접" 그 페이지를 열었을 때만 작동하며, 스스로 페이지를 열거나 클릭하거나
claude.ai 에 자동으로 접속하지 않습니다. 그래서 "설정 > 사용량"을 열 때마다 숫자가
업데이트됩니다. 바로가기: 창의 "사용량 페이지 열어 업데이트" 버튼, 트레이 메뉴 > 지금 업데이트,
또는 확장 프로그램 도구 모음 버튼. 모든 데이터는 내 컴퓨터에만 있습니다.

브라우저별
----------
Chrome  : chrome://extensions → 오른쪽 위 "개발자 모드" 켜기 →
          "압축해제된 확장 프로그램을 로드합니다" → 경로 붙여넣기 (Ctrl+V) → 폴더 선택.
Edge    : edge://extensions → 왼쪽 "개발자 모드" 켜기 → "압축 풀린 파일 로드" → 경로 붙여넣기 → 폴더 선택.
Opera   : opera://extensions → "개발자 모드" → "압축해제된 확장 프로그램 로드" → 경로 붙여넣기.
Brave   : brave://extensions → "개발자 모드" → "압축해제된 확장 프로그램을 로드합니다" → 경로 붙여넣기.
Vivaldi : vivaldi://extensions → "개발자 모드" → "압축해제된 확장 프로그램을 로드합니다" → 경로 붙여넣기.
그 밖의 Chromium 기반 브라우저도 같은 방법입니다.
폴더 위치: %LOCALAPPDATA%\ClaudeUsageTray\extension
이후에는 삭제하거나 옮기지 마세요. 브라우저 시작 시 "개발자 모드 확장 프로그램 사용 중지"
알림이 뜨면 닫으면 됩니다.

FIREFOX
-------
Firefox 는 Mozilla 서명이 있는 추가 기능만 영구 보관하므로 3가지 방법이 있습니다.
기본 브라우저가 Firefox 이면 설치 프로그램이 어느 쪽을 쓸지 묻습니다.
 1) 임시 설치 (계정 불필요, 10초): about:debugging#/runtime/this-firefox →
    "임시 부가 기능 로드…" → extension-firefox\manifest.json 선택 (경로는 클립보드에 있음).
    Firefox 를 닫으면 사라지고, 실행할 때마다 다시 해야 합니다.
 2) 영구 설치 (무료): addons.mozilla.org 가입 → 개발자 허브 → "새 부가 기능 제출" →
    "직접 배포"(On your own / unlisted) → claude-usage-bridge-firefox.xpi 업로드.
    몇 분 안에 Mozilla 가 서명하며, 서명된 .xpi 를 Firefox 로 끌어다 놓으면 영구 사용됩니다.
 3) Firefox Developer Edition / Nightly / ESR: about:config 에서
    xpinstall.signatures.required 를 false 로 바꾼 뒤 about:addons > 톱니바퀴 >
    "파일에서 부가 기능 설치…" 로 .xpi 를 선택합니다. 일반 Firefox 에서는 불가능합니다.
가장 쉬운 대안: Firefox 는 그대로 쓰고 Chrome 또는 Edge 에도 확장 프로그램을 한 번 설치하세요
(브라우저 하나에만 설치돼 있으면 됩니다).

사용법
------
* 트레이 아이콘 왼쪽 클릭: 작은 창 표시 / 숨김.
* 오른쪽 클릭: 지금 업데이트, 표시 모드, 언어, Windows 시작 시 실행, 도움말, 제거, 종료.
* 표시 모드 "자동"은 브라우저의 claude.ai 와 Claude Code 중 쓰는 쪽에 맞춰 바뀌고,
  "고정"은 항상 claude.ai 를 보여 줍니다.
* 세션 또는 주간 한도가 80%, 90%, 95% 에 도달하면 알림이 뜹니다.
* 트레이 아이콘은 사용 비율을 보여 주며 찰수록 붉어집니다.

언어
----
언어는 Windows 설정에 따라 자동 선택되며 트레이 메뉴 > 언어 에서 바꿀 수 있습니다.
영어, 번체 중국어, 간체 중국어, 일본어, 한국어가 들어 있습니다. 언어를 추가하려면
lang\en.json, lang\en.cmd, docs\README.en.txt 를 fr.json / fr.cmd / README.fr.txt 처럼
복사해 번역한 뒤 다시 시작하세요. 메뉴에 자동으로 나타납니다.
설치 프로그램 언어 지정: START_HERE_Install.bat ja

설정
----
파일: %USERPROFILE%\.claude_usage_tray\config.json (처음 실행 후 생성)
  thresholds    알림 기준, 기본 [80, 90, 95]
  stale_minutes  이 시간(분)이 지나면 업데이트를 알려 줍니다, 기본 60
  language      "auto" 또는 "ko" 같은 코드
  browsers / code_apps  사용 중인 앱을 판단하는 프로세스 이름

제거
----
다음 중 하나: 트레이 메뉴 > "제거…" / UNINSTALL.bat 더블클릭 /
%LOCALAPPDATA%\ClaudeUsageTray\uninstall.bat 실행. 프로그램을 종료하고 자동 시작과
모든 파일을 삭제하며, 브라우저 확장 프로그램 페이지를 열어 "Claude Usage Bridge" 를
제거할 수 있게 합니다. (Python 과 패키지는 그대로 둡니다. 필요하면 Windows 설정 > 앱에서 삭제.)

업데이트
--------
새 버전을 풀고 START_HERE_Install.bat 을 다시 실행하세요. 확장 프로그램이 바뀌었다면
브라우저 확장 프로그램 페이지에서 다시 로드합니다.

문제 해결
---------
* Chrome / Edge 142 이상에서 숫자가 안 나오거나 "로컬 네트워크" 접근을 묻는 경우:
  확장 프로그램 페이지 → Claude Usage Bridge → "세부정보" → "사이트 설정" →
  "로컬 네트워크 액세스"를 "허용"으로. (이 PC 자신과만 통신합니다.)
* 계속 "데이터 없음": 확장 프로그램이 켜져 있고 그 브라우저에서 claude.ai 에 로그인했는지
  확인한 뒤 그 브라우저에서 "설정 > 사용량"을 여세요.
* 창이 안 보임: 트레이의 ^ 안을 확인하세요.
* Python 을 찾을 수 없음: python.org 에서 설치(Add python.exe to PATH 체크)한 뒤 다시 실행.
* claude.ai 개편 후 숫자가 이상함: 페이지 해석 로직 업데이트가 필요할 수 있습니다.

참고
----
비공식 도구이며 Anthropic 과 무관합니다. 표시되는 비율은 claude.ai 페이지의 값 그대로이며,
Anthropic 은 정확한 메시지 수를 공개하지 않습니다.
