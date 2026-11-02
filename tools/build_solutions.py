#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成三张买方场景页 + /solutions/ 索引。

路径（与现有产品页并列，不改产品页的两段式结构）：

    /solutions/                              索引
    /solutions/compute-center-ops/           智算中心运营 → BOSS
    /solutions/enterprise-ai-gateway/        企业级 AI 网关 → AIRouter
    /solutions/gov-ai-training-inference/    政务与行业训推 → Rune

正文只复述首页与产品页已经公开的能力。不写未发布功能、客户名、示意面板里的数字。
MCP 只作为采购用语的对齐说明，不写成已交付模块。

CTA 只指向站内产品页、/contact、文档站，以及首页已经公开的 rune 子域。
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import seo  # noqa: E402
from portal_page import (Ctx, brand_action, derive, esc, ext, finish_many,  # noqa: E402
                         overline, upstream_brand)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CSS = 'solutions.css'

CONTACT = '/contact'
DOCS = 'https://docs.poxiaoshi.cn/'
RUNE_HOST = 'https://rune.poxiaoshi.cn/'

# 允许出现在场景页正文里的 href。写死在渲染数据之外，守卫拿它当白名单，
# 不从 PAGES 里现算——改漏一个落点会红，而不是跟着数据一起改绿。
ALLOWED_HREFS = {
    '/',
    CONTACT,
    '/faq/',
    '/faq/#faq-boss',
    '/faq/#faq-airouter',
    '/faq/#faq-rune',
    '/products/boss/',
    '/products/ai-router/',
    '/products/rune/',
    '/products/moha/',
    '/solutions/',
    '/solutions/compute-center-ops/',
    '/solutions/enterprise-ai-gateway/',
    '/solutions/gov-ai-training-inference/',
    DOCS,
    RUNE_HOST,
}


def links(pairs):
    return '<p class="tf-sol-links">' + ''.join(
        '<a href="%s"%s>%s</a>' % (href, ext(href), esc(label))
        for label, href in pairs) + '</p>'


def crumb(parts):
    """parts: [(label, href or None), …]，最后一项是当前页。"""
    bits = []
    for i, (label, href) in enumerate(parts):
        if i:
            bits.append('<span aria-hidden="true">/</span>')
        if href:
            bits.append('<a href="%s">%s</a>' % (href, esc(label)))
        else:
            bits.append('<span>%s</span>' % esc(label))
    return '<nav class="tf-sol-crumb" aria-label="面包屑">%s</nav>' % ''.join(bits)


def table(rows):
    body = []
    for feature, effect in rows:
        body.append(
            '<tr><td data-label="已公开能力">%s</td><td data-label="可感知的效果">%s</td></tr>'
            % (esc(feature), esc(effect)))
    return (
        '<div class="tf-sol-table-wrap"><table class="tf-sol-table">'
        '<thead><tr><th>已公开能力</th><th>可感知的效果</th></tr></thead>'
        '<tbody>%s</tbody></table></div>' % ''.join(body))


def steps(items):
    lis = ''.join('<li><b>0%d</b>%s</li>' % (i, esc(label))
                  for i, label in enumerate(items, start=1))
    return '<ol class="tf-sol-steps">%s</ol>' % lis


def bullets(items):
    return '<ul class="tf-sol-list">' + ''.join(
        '<li><strong>%s</strong> %s</li>' % (esc(who), esc(text)) for who, text in items
    ) + '</ul>'


def hero(kicker, h1, lede, actions, trail):
    buttons = ''.join(brand_action(label, href, kind) for label, href, kind in actions)
    return (
        '<header class="tf-sol-wrap tf-sol-hero tf-motion-section is-motion-visible" '
        'style="--tf-motion-order: 0;">'
        + crumb(trail)
        + overline(kicker)
        + '<h1 class="tf-sol-title">%s</h1>' % esc(h1)
        + '<p class="tf-sol-lede">%s</p>' % esc(lede)
        + '<div class="tf-sol-actions">%s</div></header>' % buttons)


def block(order, title, inner, last=False):
    extra = ' tf-sol-end' if last else ''
    return (
        '<section class="tf-sol-wrap tf-sol-block%s tf-motion-section" '
        'style="--tf-motion-order: %d;">'
        '<h2 class="tf-sol-h2">%s</h2>%s</section>'
        % (extra, order, esc(title), inner))


def page_shell(inner):
    return '<div class="tf-solutions-page">%s</div>' % inner


# ---------------------------------------------------------------- 三张场景页
BOSS_LEDE = (
    '算力中心一年的运营，往往卡在三件事：租户怎么开、配额怎么切、月底怎么对账。'
    '值班同学在表格和工单里来回找，资源水位和网关质量分散在不同系统。'
    '招标书里写「运营服务」，买方要的是：开户、分配、计量、报表能闭环，'
    '且说得出平台当下是否健康。')
BOSS_DESC = '算力中心一年的运营，往往卡在三件事：租户怎么开、配额怎么切、月底怎么对账。'

GATEWAY_LEDE = (
    '应用侧要同时打到自建推理与多家公有云模型时，密钥散落、协议各异、限额各管各的。'
    '招标与内部立项里常见「AI 网关 / 大模型代理」一类表述：要的是统一入口、可审核、'
    '可选路、可计量。AIRouter 把这件事收成控制面配置与数据面转发。')
GATEWAY_DESC = (
    '应用侧要同时打到自建推理与多家公有云模型时，密钥散落、协议各异、限额各管各的。')
GATEWAY_NOTE = (
    '公开招标常写 MCP 代理、Agent 代理。官网当前公开能力落在统一接入、协议适配、'
    '策略路由、限额与审计。本页用这些买方用语对齐检索，正文只陈述上述已公开能力。')

GOV_LEDE = (
    '政务与行业侧上大模型，常见诉求是：有一块可用的训推资源池，任务能提交、'
    '配额看得见、工作空间能隔离，私有化或离线也能交。采购文件里写「算力租用」'
    '「配套算力」「训推平台」，落到平台侧，缺的往往是控制面——谁在哪个池子用了多少卡、'
    '任务卡在哪一步、服务是否已注册到网关。')
GOV_DESC = (
    '政务与行业侧上大模型，常见诉求是：有一块可用的训推资源池，任务能提交、'
    '配额看得见、工作空间能隔离，私有化或离线也能交。')


def boss_page():
    trail = [('首页', '/'), ('解决方案', '/solutions/'), ('智算中心运营', None)]
    inner = hero(
        'BOSS · 智算中心运营_',
        '智算中心运营：租户、配额与出账在同一控制台',
        BOSS_LEDE,
        [('看 BOSS 产品', '/products/boss/', 'primary'),
         ('预约演示', CONTACT, 'secondary')],
        trail)
    inner += block(1, '现场常见的缺口', bullets([
        ('运营值班', '少一张把风险待办、容量水位、网关质量放在一起的视图，开口先要翻多个后台。'),
        ('平台管理员', '少按租户、资源池与队列统一下发配额、超限自动拦截的路径，靠人工台账卡额度。'),
        ('财务与结算', '少 GPU 时长、存储与调用量的实时计量与按月出账导出，核销依赖二次汇总。'),
    ]))
    inner += block(2, '已公开能力', table([
        ('租户、组织与成员在一个入口完成开户与权限下发', '开户与权限下发走同一入口'),
        ('按租户、资源池与队列分配算力配额，超限自动拦截', '超额占用可在配额策略层被拦住'),
        ('GPU 时长、存储与调用量实时计量，按月出账并可导出', '出账有据可查，月底少一轮二次汇总'),
        ('值班视图汇总风险待办、容量水位、网关质量、资产与账号概览',
         '值班先看一张摘要，再进对应处置入口'),
        ('汇总 Rune、Moha、AIRouter 侧事实，不重建各产品的业务数据',
         '运营面与业务面各管一段账'),
    ]))
    inner += block(3, '一条运营路径', steps(['开户与授权', '配额与调度', '计量与出账']))
    inner += block(4, '下一步', links([
        ('BOSS 产品页', '/products/boss/'),
        ('预约演示', CONTACT),
        ('产品定义', '/faq/#faq-boss'),
        ('企业级 AI 网关', '/solutions/enterprise-ai-gateway/'),
        ('政务与行业训推', '/solutions/gov-ai-training-inference/'),
    ]), last=True)
    return page_shell(inner)


def gateway_page():
    trail = [('首页', '/'), ('解决方案', '/solutions/'), ('企业级 AI 网关', None)]
    inner = hero(
        'AIRouter · 企业级 AI 网关_',
        '企业级 AI 网关：多家上游，一个兼容入口',
        GATEWAY_LEDE,
        [('看 AIRouter 产品', '/products/ai-router/', 'primary'),
         ('预约演示', CONTACT, 'secondary')],
        trail)
    inner += block(1, '现场常见的缺口', bullets([
        ('应用与平台研发', '少一个 OpenAI / Claude 风格的统一调用入口，每换一家上游就要改一套客户端。'),
        ('安全与合规', '少认证、审核与策略选路的集中关口，调用是否授权、走哪条渠道说不清。'),
        ('运营与成本', '少按次保留的用量与审计记录，调用对账靠各上游后台拼表。'),
    ]))
    inner += block(2, '已公开能力', table([
        ('一个入口接入集群内自建推理与公有云模型', '调用方更换 base URL 与密钥即可切流'),
        ('兼容 OpenAI、Claude 风格接口，网关按上游方言转发', '上游差异收在网关侧'),
        ('认证、审核、选路、限额', '未授权与超限请求可在入口拦截'),
        ('控制面管配置与落库，数据面只管转发', '配置变更与转发路径分开，便于排障'),
        ('保留每一次调用的用量与审计记录', '调用量、渠道与策略结果可回看'),
    ]))
    inner += block(3, '一次请求的路径', steps(['认证与审核', '选出渠道', '转发计量']))
    inner += block(4, '与 MCP、Agent 代理一类采购用语',
                   '<p class="tf-sol-note">%s</p>' % esc(GATEWAY_NOTE))
    inner += block(5, '下一步', links([
        ('AIRouter 产品页', '/products/ai-router/'),
        ('预约演示', CONTACT),
        ('产品定义', '/faq/#faq-airouter'),
        ('智算中心运营', '/solutions/compute-center-ops/'),
        ('政务与行业训推', '/solutions/gov-ai-training-inference/'),
    ]), last=True)
    return page_shell(inner)


def gov_page():
    trail = [('首页', '/'), ('解决方案', '/solutions/'), ('政务与行业训推', None)]
    inner = hero(
        'Rune · 政务与行业训推_',
        '政务与行业训推：任务、推理与算力配额一套控制面',
        GOV_LEDE,
        [('看 Rune 产品', '/products/rune/', 'primary'),
         ('预约演示', CONTACT, 'secondary')],
        trail)
    inner += block(1, '现场常见的缺口', bullets([
        ('业务与模型团队', '少一次提交贯通资源申请、训练、调优、推理与部署的路径，流程拆在多个工单系统。'),
        ('平台与运维', '少按工作空间隔离、按规格选池、按配额拦截的控制面，卡时与任务状态要事后对人。'),
        ('采购与运营方', '少算力配额与用量结构可回看的记录，续签与扩容时说不清用在哪。'),
    ]))
    inner += block(2, '已公开能力', table([
        ('接入集群、隔离工作空间、定义资源规格、下发配额', '多团队共用资源池时边界清楚'),
        ('上层是训练、微调、推理与应用实例，下层是 Kubernetes', '交付形态贴近云原生运维习惯'),
        ('把模型服务注册到网关', '推理实例可进入统一调用链路，与 AIRouter 衔接'),
        ('支持私有化与离线交付', '适合对部署边界有要求的政务与行业机房'),
        ('以云原生为统一基座，兼容国产服务器、操作系统与算力芯片',
         '可按现有国产机房环境做私有化交付'),
    ]))
    inner += block(3, '从提交到实例就绪', steps(['提交规格', '选资源池', '实例就绪']))
    inner += block(4, '下一步', links([
        ('Rune 产品页', '/products/rune/'),
        ('文档', DOCS),
        ('Rune 控制台', RUNE_HOST),
        ('预约演示', CONTACT),
        ('产品定义', '/faq/#faq-rune'),
        ('同时看运营出账', '/solutions/compute-center-ops/'),
        ('资产入库看 Moha', '/products/moha/'),
    ]), last=True)
    return page_shell(inner)


INDEX_LEDE = (
    '三页面向招标与立项里常见的买方用语：智算中心运营、企业级 AI 网关、'
    '政务与行业训推。每页只复述官网已公开的能力，并链到对应产品页与联系页。')
INDEX_DESC = INDEX_LEDE


def index_page():
    trail = [('首页', '/'), ('解决方案', None)]
    cards = (
        ('/solutions/compute-center-ops/', 'BOSS',
         '智算中心运营：租户、配额与出账在同一控制台',
         '开户、配额、计量与值班视图，面向智算中心运营方。'),
        ('/solutions/enterprise-ai-gateway/', 'AIRouter',
         '企业级 AI 网关：多家上游，一个兼容入口',
         '统一接入、协议适配、策略路由、限额与审计。'),
        ('/solutions/gov-ai-training-inference/', 'Rune',
         '政务与行业训推：任务、推理与算力配额一套控制面',
         '工作空间隔离、配额下发、私有化与离线交付。'),
    )
    card_html = ''.join(
        '<a class="tf-sol-card" href="%s"><small>%s</small><h2>%s</h2><p>%s</p></a>'
        % (href, esc(kicker), esc(title), esc(copy))
        for href, kicker, title, copy in cards)
    inner = (
        '<header class="tf-sol-wrap tf-sol-hero tf-motion-section is-motion-visible" '
        'style="--tf-motion-order: 0;">'
        + crumb(trail)
        + overline('解决方案_')
        + '<h1 class="tf-sol-title">按采购场景看晓石云</h1>'
        + '<p class="tf-sol-lede">%s</p>' % esc(INDEX_LEDE)
        + '<div class="tf-sol-cards">%s</div>' % card_html
        + links([
            ('十条产品定义', '/faq/'),
            ('预约演示', CONTACT),
        ])
        + '</header>')
    return page_shell(inner)


PAGES = (
    {
        'out_rel': 'solutions/index.html',
        'depth': 1,
        'title': '解决方案 | 破晓石科技',
        'description': INDEX_DESC,
        'h1': '按采购场景看晓石云',
        'crumb_name': '解决方案',
        'markup': index_page,
        'trail': [('首页', seo.SITE_URL + '/'), ('解决方案', None)],
    },
    {
        'out_rel': 'solutions/compute-center-ops/index.html',
        'depth': 2,
        'title': '智算中心运营 | 破晓石科技',
        'description': BOSS_DESC,
        'h1': '智算中心运营：租户、配额与出账在同一控制台',
        'crumb_name': '智算中心运营',
        'markup': boss_page,
        'trail': [('首页', seo.SITE_URL + '/'),
                  ('解决方案', seo.abs_url('solutions/')),
                  ('智算中心运营', None)],
    },
    {
        'out_rel': 'solutions/enterprise-ai-gateway/index.html',
        'depth': 2,
        'title': '企业级 AI 网关 | 破晓石科技',
        'description': GATEWAY_DESC,
        'h1': '企业级 AI 网关：多家上游，一个兼容入口',
        'crumb_name': '企业级 AI 网关',
        'markup': gateway_page,
        'trail': [('首页', seo.SITE_URL + '/'),
                  ('解决方案', seo.abs_url('solutions/')),
                  ('企业级 AI 网关', None)],
    },
    {
        'out_rel': 'solutions/gov-ai-training-inference/index.html',
        'depth': 2,
        'title': '政务与行业训推 | 破晓石科技',
        'description': GOV_DESC,
        'h1': '政务与行业训推：任务、推理与算力配额一套控制面',
        'crumb_name': '政务与行业训推',
        'markup': gov_page,
        'trail': [('首页', seo.SITE_URL + '/'),
                  ('解决方案', seo.abs_url('solutions/')),
                  ('政务与行业训推', None)],
    },
)


def highlight_solutions(doc):
    """桌面顶层「解决方案」亮起。chrome 比对前会抹掉 is-active。"""
    def repl(m):
        tag = m.group(0)
        if 'href="/solutions/"' not in tag or 'is-active' in tag:
            return tag
        return tag.replace('class="tf-nav-menu-link "',
                           'class="tf-nav-menu-link is-active "', 1)
    return re.sub(r'<a\b[^>]*class="tf-nav-menu-link "[^>]*>', repl, doc)


def guards(ctx, spec, doc, main_html):
    rel = spec['out_rel']

    def miss(msg):
        ctx.miss.append('%s: %s' % (rel, msg))

    if main_html.count('<h1') != 1:
        miss('应有且仅有一个 h1')
    if esc(spec['h1']) not in main_html:
        miss('h1 不在正文里')
    if esc(spec['description']) not in main_html:
        miss('description 不在可见正文里')
    if 'aria-label="面包屑"' not in main_html:
        miss('缺少可见面包屑')
    if esc(spec['crumb_name']) not in main_html:
        miss('面包屑当前页名称不可见')
    hrefs = re.findall(r'href="([^"]+)"', main_html)
    for href in hrefs:
        if href not in ALLOWED_HREFS:
            miss('正文链接不在白名单: ' + href)
    for banned in ('价值是', '赋能', '抓手', '充值', '扣费', '余额'):
        if banned in main_html:
            miss('禁用词: ' + banned)
    if re.search(r'不是.{0,40}而是', main_html):
        miss('出现「不是…而是…」')
    if upstream_brand(doc):
        miss('上游品牌名')
    # 示意面板上的客户化名字与百分比，不进场景页。
    for leaked in ('edu-university', 'energy-makinu', 'gov-datacenter', '环比 +12%',
                   '1.24 P'):
        if leaked in main_html:
            miss('带进了首页示意数据: ' + leaked)
    if doc.count('class="tf-nav-menu-link is-active "') != 1:
        miss('桌面「解决方案」应恰好亮起一处')
    if 'href="https://ppt.poxiaoshi.cn/' in doc:
        miss('导航仍指向路演站')


def main():
    ctx = Ctx()
    built = []
    home_len = home_md5 = 0
    for spec in PAGES:
        markup = spec['markup']()
        doc, home, home_md5 = derive(
            ctx,
            out_rel=spec['out_rel'],
            title=spec['title'],
            description=spec['description'],
            extra_css=CSS,
            main_markup=markup,
            active_group=None,
            main_label='main body -> %s' % spec['out_rel'],
            nav_label='nav active state -> 解决方案',
            depth=spec['depth'],
            seo_extra=dict(extra_jsonld=(seo.breadcrumb(spec['trail']),)),
        )
        doc = highlight_solutions(doc)
        home_len = len(home)
        guards(ctx, spec, doc, markup)
        built.append((os.path.join(ROOT, spec['out_rel']), spec['out_rel'], doc))
    finish_many(ctx, built, home_len, home_md5,
                extra_lines=['solutions: %s' % ', '.join(s['out_rel'] for s in PAGES)])


if __name__ == '__main__':
    sys.stdout.reconfigure(line_buffering=True)
    main()
