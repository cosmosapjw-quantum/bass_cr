# Grackle Savin2002 H/D CX 기계적 source intake

관측 2026-10-24 01:56–01:58 UTC /10:56–10:58 KST. 공식 grackle-project/grackle main 현재 commit을6d57fe2c3eb07c34dadb0b0e568cdc12f975146d로pin했다. Commit metadata 날짜2026-09-15T13:08:54Z. COMMIT.json에원문보존. 과학실행/수치평가/원격쓰기0.

## 코드에서 직접 관측한 사실

src/clib/rate_functions.c lines599–618:

- k50: HII+DI→HI+DII. T<=2e5K이면 `(2.0e-10*pow(T,0.402)*exp(-37.1/T)-3.31e-17*pow(T,1.48))/units`.
- k50: T>2e5K이면 `2.5e-8*pow(T/2e5,0.402)/units`. 주석은상온도에서extrapolate한다고명시한다.
- k51: HI+DII→HII+DI. 모든입력T에 `(2.06e-10*pow(T,0.396)*exp(-33.0/T)+2.03e-9*pow(T,-0.332))/units`를반환한다. Reverse의두번째powerterm이존재한다.
- 양쪽주석은Savin2002fit이T<2e5K에유효하다고쓴다. Function자체에lowerTcutoff,positiveclamp,max(tiny,rate),Tvalidation은없다. k51에는upperTbranch도없다.
- 초기tablewrapper src/clib/initialize_rates.c: add_reaction_rate는configuredTemperatureStart→TemperatureEnd의loggrid에서함수를호출한다. 각slot을tiny로초기화하지만곧 `(*rate_ptr)[i]=my_function(T,units,my_chemistry)`로무조건덮어쓴다. 따라서이초기tiny대입은k50/k51의positivityclamp가아니다. lines340–341에서k50/k51을그wrapper에등록한다.
- doc/source/RateFunctions.rst는T를K,units=1일때CGS반환이라고명시한다.

원Savin논문과계수/적합유효하한/물리단위·모형의독립일치여부는이작업에서판정하지않았다. 원식을정확하게재현한다는판정은controller가원논문과비교해내린다. 위는실제C구현의literal식과분기다. 전체solver후단의모든clamp/보간경로를전수추적한주장도하지않는다.

## 라이선스

동일pin의LICENSE전문을보존했다. 파일상단은EnzoPublicLicense를BSD-like라고설명하며,UniversityofIllinois/NCSA와UniversityofCalifornia/BSD조건·저작권·면책을포함한다. 복제/수정/배포가허용되며source/binary배포의저작권·조건·면책보존및endorsement제한이명시되어있다. 정확한조건은동봉LICENSE전문을사용한다.

## 원문 경로

- https://github.com/grackle-project/grackle/commit/6d57fe2c3eb07c34dadb0b0e568cdc12f975146d
- https://github.com/grackle-project/grackle/blob/6d57fe2c3eb07c34dadb0b0e568cdc12f975146d/src/clib/rate_functions.c
- https://github.com/grackle-project/grackle/blob/6d57fe2c3eb07c34dadb0b0e568cdc12f975146d/src/clib/initialize_rates.c
- https://github.com/grackle-project/grackle/blob/6d57fe2c3eb07c34dadb0b0e568cdc12f975146d/doc/source/RateFunctions.rst
- https://github.com/grackle-project/grackle/blob/6d57fe2c3eb07c34dadb0b0e568cdc12f975146d/LICENSE

선택원문은경로separator를doubleunderscore로바꿔보존했다. solve_rate_cool_g.F와cool1d_multi_g.F도획득했으나이보고의k50/k51함수판정은rate_functions.c와initializetablewrapper에한정한다.
