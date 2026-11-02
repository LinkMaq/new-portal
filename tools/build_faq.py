#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 /faq/ —— 十条产品定义问答 + FAQPage JSON-LD。

可见正文与结构化数据共用下面的 FAQ 元组：问题、答案、锚点各写一次。
`seo.faq_page()` 吃同一份元组，`qa/seo.py` 再拿产物两边对账，避免
「页面一套、JSON-LD 另一套」。

文案来自已公开的产品口径（首页 FAQ、产品页 lede、板块正文），不新增
未发布的功能、客户或数字。首页原有 9 问保持原样并另挂锚点；这一页补上
AIRouter / XCMP 等可单独引用的定义句。
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import seo  # noqa: E402
from portal_page import Ctx, derive, esc, ext, finish, overline, upstream_brand  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT_REL = 'faq/index.html'
OUT = os.path.join(ROOT, 'faq', 'index.html')
CSS = 'faq.css'

TITLE = '常见问题 | 破晓石科技'
DESCRIPTION = ('十条产品定义问答，复述晓石云已公开的 Rune、Moha、AIRouter、BOSS、'
               'XCMP 与 Rune Harness 口径。')

# (anchor, question, answer, [(href, label), …])
# answer 进可见 <p class="tf-faqpage-a">，也原样进 JSON-LD。相关链接在段落外面，
# 不掺进 acceptedAnswer。
FAQ = (
    ('faq-matrix',
     '晓石云的产品矩阵覆盖哪些场景？',
     '晓石云的产品矩阵由四大核心板块组成：Rune 承载 AI 训推，Moha 沉淀模型与数据资产，'
     'AIRouter 做 AI 聚合网关，BOSS 面向智算中心运营方提供租户、配额与计量管理；'
     'XCMP 为四大板块提供多云资源底座，并共同向 Rune Harness 云智算内核演进。',
     (('/solutions/', '按场景查看'), ('/', '回到首页'))),
    ('faq-rune',
     'Rune 是什么？',
     'Rune 是晓石云的多租户 AI 训推平台控制面：训练任务、推理服务与算力配额在同一处编排，'
     '可接入集群、隔离工作空间、定义资源规格、下发配额，并把模型服务注册到网关；'
     '下层基于 Kubernetes，支持私有化与离线交付。',
     (('/products/rune/', 'Rune 产品页'),
      ('/solutions/gov-ai-training-inference/', '政务与行业训推'))),
    ('faq-moha',
     'Moha 是什么？',
     'Moha 是晓石云的私有化数字资产仓：模型、数据集、镜像与 Space 共用一个元数据面，'
     '版本采用 Git 语义，大文件走 LFS，镜像兼容 OCI，需要保密的上传可加密入库，'
     '资产可检索、可追溯。',
     (('/products/moha/', 'Moha 产品页'),)),
    ('faq-airouter',
     'AIRouter 是什么？',
     'AIRouter 是晓石云的 AI 聚合网关：一个入口接入集群内自建推理服务与公有云模型，'
     '调用方可用 OpenAI 或 Claude 风格接口，网关负责认证、审核、选路与限额，'
     '并保留每一次调用的用量与审计记录；控制面管配置与落库，数据面只管转发。',
     (('/products/ai-router/', 'AIRouter 产品页'),
      ('/solutions/enterprise-ai-gateway/', '企业级 AI 网关'))),
    ('faq-boss',
     'BOSS 面向谁？做什么？',
     'BOSS 面向智算中心与平台的运营方：租户开户与授权、算力配额分配、'
     'GPU 时长与存储计量、按月出账与运营报表，在同一控制台完成；'
     '它汇总风险待办、容量水位、网关质量等值班视图，不重建 Rune、Moha、AIRouter 各自的业务事实。',
     (('/products/boss/', 'BOSS 产品页'),
      ('/solutions/compute-center-ops/', '智算中心运营'))),
    ('faq-xcmp',
     'XCMP 在产品体系里起什么作用？',
     'XCMP 是晓石云的多云资源管理底座，可识别并接入 Kubernetes、vCenter、OpenStack、'
     '华为云等平台，向下承接多云资源，向上支撑 Rune、Moha、AIRouter、BOSS，'
     '并参与向 Rune Harness 云智算内核的演进。',
     (('/products/rune/', 'Rune 产品页'),)),
    ('faq-harness',
     'Rune Harness 云智算内核是什么？',
     'Rune Harness 是晓石云正在规划的平台级智能操作内核，由 Tenant Harness 与 '
     'BOSS Harness 两个隔离安全域组成，统一会话、资源发现、诊断、变更计划、审批与执行追踪；'
     '它不重建各领域事实，也不持有底层长期凭据，写操作一律走 Plan → Approval → Apply。',
     (('/#faq-harness', '首页上的同一问'),)),
    ('faq-integration',
     '能否对接现有云平台与开发框架？',
     '可以。AIRouter 兼容 OpenAI 等主流接口协议，替换 base URL 即可接入；'
     'XCMP 可自动识别并接入 Kubernetes、vCenter、OpenStack、华为云等；'
     'Rune 兼容主流训练框架与 Transformer 生态，并提供集成 IDE 与桌面仿真环境。',
     (('/products/ai-router/', 'AIRouter 产品页'),
      ('/products/rune/', 'Rune 产品页'))),
    ('faq-delivery',
     '晓石云与常见公有云方案有何交付差异？',
     '晓石云以云原生为统一基座，自研 KubeGems 等开源项目，平台全栈采用 Golang，'
     '兼容国产服务器、操作系统与算力芯片，可完全私有化交付。',
     (('/about', '公司简介'), ('/contact', '预约演示'))),
    ('faq-trial',
     '如何获取产品与试用？',
     'Rune、Moha、AIRouter 与 BOSS 均已提供商业版，XCMP 云管理能力随平台交付；'
     '可通过官网联系页预约演示，团队会在一个工作日内联系，并安排交流。'
     '入口：https://www.poxiaoshi.cn/contact/',
     (('/contact', '联系页'),)),
)


def item(anchor, question, answer, links):
    related = ''.join(
        '<a href="%s"%s>%s</a>' % (href, ext(href), esc(label))
        for href, label in links)
    return (
        '<li id="%s" class="tf-faqpage-item scroll-mt-[132px]">'
        '<h2 class="tf-faqpage-q">%s</h2>'
        '<p class="tf-faqpage-a">%s</p>'
        '<p class="tf-faqpage-more">%s</p>'
        '</li>' % (esc(anchor), esc(question), esc(answer), related))


def main_markup():
    items = ''.join(item(*row) for row in FAQ)
    # 栏宽、居中、页首内边距走全站 .tf-section-inner，不另写一套 760px 容器。
    # 列表若再设 width 再把 margin 归零，会钉在视口左侧（2026-11-02）。
    return (
        '<div class="tf-faqpage">'
        '<section class="tf-section scroll-mt-[132px] text-white '
        'tf-motion-section is-motion-visible" style="--tf-motion-order: 0;">'
        '<div class="tf-section-inner tf-section-frame">'
        '<header class="tf-faqpage-hero">'
        '<nav class="tf-faqpage-crumb" aria-label="面包屑">'
        '<a href="/">首页</a><span aria-hidden="true">/</span><span>常见问题</span>'
        '</nav>'
        + overline('FAQ_') +
        '<h1 class="tf-section-title mt-5">产品定义，十条可以单独引用</h1>'
        '<p class="tf-section-copy">%s</p>'
        '</header>'
        '<ol class="tf-faqpage-list">%s</ol>'
        '</div></section></div>' % (esc(DESCRIPTION), items))


def guards(ctx, doc):
    def miss(msg):
        ctx.miss.append('faq: ' + msg)

    if doc.count('<h1') != 1:
        miss('应有且仅有一个 h1')
    if DESCRIPTION not in doc:
        miss('导语不在页面上')
    if '<div class="tf-section-inner tf-section-frame">' not in doc.split('<main', 1)[-1]:
        miss('FAQ 未放进全站 section 栏')
    ids = re.findall(r'<li id="([^"]+)" class="tf-faqpage-item[^"]*">', doc)
    if ids != [row[0] for row in FAQ]:
        miss('锚点顺序不对: %s' % ids)
    for anchor, question, answer, links in FAQ:
        if '<h2 class="tf-faqpage-q">%s</h2>' % esc(question) not in doc:
            miss('问题不可见: ' + question)
        if '<p class="tf-faqpage-a">%s</p>' % esc(answer) not in doc:
            miss('答案不可见: ' + anchor)
        for href, label in links:
            anchor = '<a href="%s"%s>%s</a>' % (href, ext(href), esc(label))
            if anchor not in doc:
                miss('相关链接不对: %s -> %s' % (label, href))
    # 结构化数据与可见答案同源。期望值来自 FAQ 元组，不从 JSON 再读回来当标准。
    m = re.search(r'<script type="application/ld\+json">(.*?)</script>', doc, re.S)
    if not m:
        miss('缺少 JSON-LD')
    else:
        import json
        data = json.loads(m.group(1))
        types = [e.get('@type') for e in data.get('@graph', [])]
        if types != ['WebPage', 'FAQPage', 'BreadcrumbList']:
            miss('@graph=%s' % types)
        entity = next(e for e in data['@graph'] if e.get('@type') == 'FAQPage')
        got = [(q['name'], q['acceptedAnswer']['text'], q['@id'].split('#', 1)[1])
               for q in entity['mainEntity']]
        want = [(q, a, anchor) for anchor, q, a, _links in FAQ]
        if got != want:
            miss('JSON-LD 与 FAQ 元组不一致')
    for banned in ('价值是', '赋能', '抓手'):
        if banned in doc.split('<footer', 1)[0]:
            # 页脚站芯可能没有这些词；只扫 main 更准。footer 之前含 head，
            # JSON-LD 与可见正文都在那里。站芯页脚不含这些词。
            miss('禁用词: ' + banned)
    main = doc.split('<main', 1)[-1].split('</main>', 1)[0]
    if re.search(r'不是.{0,40}而是', main):
        miss('出现「不是…而是…」')
    if 'Rune Harness' in main:
        # 规划中的形态必须带「规划」。FAQ 第 7 条的答案里有「正在规划」。
        if main.count('正在规划') < 1:
            miss('提到 Rune Harness 时必须写明正在规划')
    if upstream_brand(doc):
        miss('上游品牌名')


def main():
    ctx = Ctx()
    url = seo.page_url(OUT_REL)
    markup = main_markup()
    doc, home, home_md5 = derive(
        ctx,
        out_rel=OUT_REL,
        title=TITLE,
        description=DESCRIPTION,
        extra_css=CSS,
        main_markup=markup,
        active_group=None,
        main_label='main body -> FAQ',
        nav_label='nav active state -> 不归属导航组',
        depth=1,
        seo_extra=dict(
            extra_jsonld=(
                seo.faq_page([(q, a, anchor) for anchor, q, a, _links in FAQ], url),
                seo.breadcrumb([
                    ('首页', seo.SITE_URL + '/'),
                    ('常见问题', None),
                ]),
            ),
        ),
    )
    guards(ctx, doc)
    finish(ctx, doc, OUT, OUT_REL, len(home), home_md5)


if __name__ == '__main__':
    sys.stdout.reconfigure(line_buffering=True)
    main()
