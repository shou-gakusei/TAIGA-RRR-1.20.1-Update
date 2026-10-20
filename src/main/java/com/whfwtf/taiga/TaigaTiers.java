package com.whfwtf.taiga;

import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.Tier;
import net.minecraft.world.item.Tiers;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraftforge.common.TierSortingRegistry;

import javax.annotation.Nullable;

/**
 * 镐子使用的挖掘等级：惰性解析 moreharvestinglevel 提供的 5/6/7 级；
 * 该模组缺席时回退到下界合金。这样 taiga3 不硬依赖 moreharvestinglevel。
 */
public final class TaigaTiers {

    private TaigaTiers() {}

    /** 等级 id（与实例内 moreharvestinglevel 一致） */
    public static final String NS = "moreharvestinglevel";

    public static Tier of(String tool) {
        return switch (tool) {
            case "dyonite" -> new LazyTier("level_5");
            case "nucleum" -> new LazyTier("level_6");
            default -> new LazyTier("level_7");
        };
    }

    /** 延迟解析的 Tier 代理：Tier 的方法都在运行期调用，此时等级已注册。 */
    private static final class LazyTier implements Tier {
        private final ResourceLocation id;
        @Nullable
        private Tier delegate;

        LazyTier(String path) {
            this.id = new ResourceLocation(NS, path);
        }

        private Tier get() {
            if (delegate == null) {
                Tier resolved = TierSortingRegistry.byName(id);
                delegate = resolved != null ? resolved : Tiers.NETHERITE;
            }
            return delegate;
        }

        @Override public int getUses() { return get().getUses(); }
        @Override public float getSpeed() { return get().getSpeed(); }
        @Override public float getAttackDamageBonus() { return get().getAttackDamageBonus(); }
        @Override public int getLevel() { return get().getLevel(); }
        @Override public int getEnchantmentValue() { return get().getEnchantmentValue(); }
        @Override public Ingredient getRepairIngredient() { return get().getRepairIngredient(); }
    }
}
