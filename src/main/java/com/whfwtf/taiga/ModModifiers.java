package com.whfwtf.taiga;

/**
 * 三个自定义特性（berserker / soul_eater / unstable）的 ID 常量。
 *
 * <p>特性本体由数据包 JSON 定义（{@code data/taiga/tinkering/modifiers/*.json}，
 * 含颜色 / max_level / 生效条件 / 文案），行为由 {@link TaigaTraitEvents} 以 Forge 事件实现。
 *
 * <p>注意：这里**不要**再用 {@code ModifierManager.ModifierRegistrationEvent} 注册静态 Modifier，
 * 否则会与 JSON 里的同名定义冲突，启动时刷屏报
 * "Dynamic modifier taiga:xxx is replacing static modifier with the same ID"。
 */
public final class ModModifiers {

    public static final String BERSERKER = "berserker";
    public static final String SOUL_EATER = "soul_eater";
    public static final String UNSTABLE = "unstable";

    private ModModifiers() {}
}
