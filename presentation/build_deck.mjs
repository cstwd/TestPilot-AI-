import fs from 'node:fs/promises';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { fileURLToPath, pathToFileURL } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.dirname(here);
const runtime = process.env.TESTPILOT_ARTIFACT_RUNTIME;
if (!runtime) throw new Error('Set TESTPILOT_ARTIFACT_RUNTIME to the bundled runtime dependencies directory.');
const skill = process.env.TESTPILOT_PRESENTATIONS_SKILL;
if (!skill) throw new Error('Set TESTPILOT_PRESENTATIONS_SKILL to the bundled Presentations skill directory.');
const modulePath = path.join(runtime, 'node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs');
const { Presentation, PresentationFile } = await import(pathToFileURL(modulePath).href);
const preview = path.join(root, '.runtime/course-final/slides');
await fs.mkdir(preview, { recursive: true });

const deck = Presentation.create({slideSize:{width:1280,height:720}});
const cn = 'Microsoft YaHei';
const color = {paper:'#F5F8FA', white:'#FFFFFF', ink:'#102638', copy:'#365168', blue:'#166F8F',
               teal:'#006D64', muted:'#5B7180', rule:'#CBD8DF', dark:'#102B3D'};
const noLine = {fill:'none',width:0,style:'solid'};
function box(slide, x, y, w, h, fill) {
  return slide.shapes.add({geometry:'rect',position:{left:x,top:y,width:w,height:h},fill,line:noLine});
}
function text(slide, value, x, y, w, h, options={}) {
  const {size=25, ink=color.ink, bold=false, align='left'}=options;
  const shape=slide.shapes.add({geometry:'textbox',fill:'none',line:noLine,
    position:{left:x,top:y,width:w,height:h}});
  shape.text=value;
  shape.text.style={typeface:cn,fontSize:size,color:ink,bold,alignment:align,
    verticalAlignment:'middle',insets:{left:0,right:0,top:0,bottom:0}};
  return shape;
}
function page(title, source) {
  const slide=deck.slides.add();
  slide.background.fill=color.paper;
  box(slide,64,48,38,5,color.teal);
  text(slide,title,64,68,1150,68,{size:46,bold:true});
  if (source) {
    box(slide,64,647,1152,1,color.rule);
    text(slide,source,64,660,1150,30,{size:16,ink:color.muted});
    slide.speakerNotes.text=source;
  }
  return slide;
}
function bullet(slide, title, body, x, y, w) {
  text(slide,title,x,y,w,39,{size:29,bold:true,ink:color.teal});
  text(slide,body,x,y+46,w,62,{size:23,ink:color.copy});
}
async function picture(slide, candidates, x,y,w,h, alt){
  for (const name of candidates) {
    let bytes;
    try { bytes=await fs.readFile(path.join(root,name)); }
    catch (err) { if (err.code === 'ENOENT') continue; throw err; }
    slide.images.add({blob:bytes,contentType:'image/png',alt,fit:'contain',
      position:{left:x,top:y,width:w,height:h}});
    return;
  }
  throw new Error('No evidence image for '+alt);
}

{
  const slide=deck.slides.add();
  slide.background.fill=color.dark;
  box(slide,80,99,80,6,'#70D7BF');
  text(slide,'TestPilot AI',80,173,1120,111,{size:93,ink:color.white,bold:true});
  text(slide,'Python 测试生成、缺陷回归与变异评估',86,304,1090,75,{size:42,ink:'#BFE8E1'});
  text(slide,'陈帅廷 · 陈万策 · 赵君豪 · 马雪朋 · 王选中',86,572,1110,51,{size:24,ink:'#ECF6F8'});
  text(slide,'课程工程汇报  /  2026.11',86,628,1000,30,{size:18,ink:'#B4CEDB'});
  slide.speakerNotes.text='开场约 25 秒。用一个 Python 缺陷说明项目目标。';
}
{
  const slide=page('产品业务流程','来源  docs/SPEC.md · docs/ARCHITECTURE.md');
  const labels=['项目与版本','AST 分析','测试生成','受限执行','缺陷回归','质量报告'];
  labels.forEach((label,i)=>{
    const x=64+i*191;
    box(slide,x,226,160,72,i===3?color.dark:'#E2EBF0');
    text(slide,label,x,226,160,72,{size:23,bold:true,
      ink:i===3?color.white:color.ink,align:'center'});
    if(i<labels.length-1)text(slide,'→',x+165,226,27,72,{size:24,ink:color.blue});
  });
  bullet(slide,'一条证据链','项目、源码版本、套件、运行和缺陷以 ID 关联。',64,366,500);
  bullet(slide,'本机模型与变异评估','Qwen3.8-27B 提供结构化生成。F13 验证存活变异与追加测试。',645,366,510);
  text(slide,'FastAPI + Jinja2  /  SQLite  /  Wasmtime + WASI CPython',64,564,1152,42,{size:24,ink:color.copy});
}
{
  const slide=page('用 AST 定位当前版本的目标函数','来源  F02 AST Studio 浏览器验收 · PHASE-02 端到端');
  await picture(slide,['reports/WP03-AST-VISUAL-001/screenshots/source-inspector.png',
    'presentation/screenshots/02-ast.png'],65,160,695,464,'真实 AST 工作台');
  bullet(slide,'不可变版本','导入原文、版本号与 SHA-256 一并保存。',815,180,390);
  bullet(slide,'源码行段','函数、类、参数、错误和行号由 Python AST 解析。',815,307,390);
  bullet(slide,'目标直达生成','将所选版本与函数传给生成工作台。',815,434,390);
}
{
  const slide=page('对同一失败节点验证修复','来源  eval/phase02 · F05 浏览器验收 · F06 实测导出');
  await picture(slide,['presentation/screenshots/05-regression.png',
    'reports/WP07-F05-001/screenshots/desktop-resolved.png'],544,166,670,424,'真实已解决缺陷详情');
  bullet(slide,'首跑记录失败','缺陷版 magnitude(-8) 返回 -8，违反明确的 doctest 期望。',64,171,444);
  bullet(slide,'WASI 执行原套件','选择较新的同名版本，保留原测试和失败节点。',64,308,444);
  bullet(slide,'质量报告可核对','查询修复后运行、实测覆盖与关联缺陷，导出 JSON。',64,445,444);
}
{
  const slide=page('F13 变异测试与反馈补测','来源  PHASE-04 F13 模块验收 · PHASE-05 反馈原始证据');
  await picture(slide,['presentation/screenshots/07-mutation.png'],64,166,694,445,'真实变异测试工作台');
  bullet(slide,'固定清单','六类算子生成候选，先验证未变异的原版。',805,178,408);
  bullet(slide,'逐项真实执行','保留杀死、存活、超时、错误和未运行。',805,306,408);
  bullet(slide,'反馈需校准','补测必须先在原版正确运行，再用同一分母复验。',805,434,408);
}
{
  const slide=page('四组变异检出率','来源  PHASE-05 冻结对照 · 10 个小项目 × 3 个种子 · 各组 117 个预登记位置');
  const summary=JSON.parse(await fs.readFile(path.join(root,'reports/phase05/summary.json'),'utf8'));
  const labels=['A  0.5B','B  模板','C  27B 初始','D  27B 补测'];
  const groups=['A','B','C','D'].map(key=>summary.groups[key]);
  slide.charts.add('bar',{
    position:{left:73,top:159,width:777,height:438},
    categories:labels,
    series:[{name:'检出率',values:groups.map(g=>Number((g.all_manifest_detection/100).toFixed(4))),fill:'#177D85',
      valuesFormatCode:'0.00%'}],
    hasLegend:false,
    dataLabels:{showValue:true,position:'outEnd',numberFormatCode:'0.00%',textStyle:{fontSize:18,fill:color.ink}},
    barOptions:{direction:'column',grouping:'clustered',gapWidth:55},
    yAxis:{min:0,max:1.0,majorUnit:0.25,numberFormatCode:'0%',textStyle:{fontSize:16},
      majorGridlines:{fill:color.rule,width:1,style:'solid'}},
    xAxis:{textStyle:{fontSize:16}},
  });
  text(slide,'104 → 105',900,236,308,96,{size:56,bold:true,ink:color.teal});
  text(slide,'27B 补测后多检出 1 个\n分母保持 117',906,343,308,110,{size:25,ink:color.copy});
  text(slide,'A 组套件未通过原版校准，整组以 0/117 计。',86,607,1124,31,{size:17,ink:color.muted});
}
{
  const slide=page('Qwen3.8-27B 本机推理','来源  PHASE-05 T01/T02 · RTX 5080 Laptop Vulkan · UD-IQ3_XXS');
  const metrics=[['10/10','连续完整且正确'],['0.553 秒','热请求首 Token 中位数'],['19.21 token/s','热请求平均吞吐'],['56/70','源码理解严格得分']];
  metrics.forEach(([number,label],i)=>{
    const x=64+(i%2)*586,y=174+Math.floor(i/2)*178;
    box(slide,x,y+138,520,1,color.rule);
    text(slide,number,x,y,540,75,{size:55,bold:true,ink:color.teal});
    text(slide,label,x,y+79,540,45,{size:27,ink:color.copy});
  });
  text(slide,'模型权重 SHA-256 已核验。API 费用为 0。',64,567,1150,47,{size:25,ink:color.ink});
}
{
  const slide=page('课程验收与分工','来源  COURSE_FINAL_REPORT.md · COURSE_TEAM_CONTRIBUTIONS.md · PHASE-04 历史回归');
  const roles=[['WP01','陈帅廷','架构与本机模型'],['WP02','陈万策','需求与工作台'],['WP03','赵君豪','AST 与测试生成'],
    ['WP04','马雪朋','WASI、缺陷与变异'],['WP05','王选中','工程工具与交付']];
  roles.forEach(([wp,name,scope],i)=>{
    const y=181+i*67;
    box(slide,64,y+58,650,1,color.rule);
    text(slide,wp,64,y,92,47,{size:23,bold:true,ink:color.teal});
    text(slide,name,168,y,117,47,{size:26,bold:true});
    text(slide,scope,300,y,300,47,{size:24,ink:color.copy});
    text(slide,'20%',622,y,88,47,{size:25,bold:true,align:'right'});
  });
  bullet(slide,'可核对的工程证据','真实 Pytest、Edge 端到端、冻结对照与独立审查。',766,175,426);
  bullet(slide,'现场展示','按源码版本、失败节点、修复回归和质量报告顺序进行。',766,311,426);
  bullet(slide,'签收','五人课程份额共 100%。项目组长人工审核另行登记。',766,447,426);
}
for(const [i,slide] of deck.slides.items.entries()){
  const png=await deck.export({slide,format:'png',scale:1});
  await fs.writeFile(path.join(preview,`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await png.arrayBuffer()));
}
const pptx=await PresentationFile.exportPptx(deck);
const build = await fs.mkdtemp(path.join(preview, 'pptx-'));
const draft = path.join(build,'draft.pptx');
const portable = path.join(build,'portable.pptx');
await pptx.save(draft);
const python = path.join(runtime,'python', process.platform === 'win32' ? 'python.exe' : 'bin/python3');
execFileSync(python, [path.join(skill,'container_tools/materialize_literal_chart_workbooks.py'),
  draft, portable, '--workspace', root, '--receipt', path.join(build,'chart-data.json')], {stdio:'inherit'});
await fs.copyFile(portable,path.join(here,'TestPilot_AI_课程汇报.pptx'));
