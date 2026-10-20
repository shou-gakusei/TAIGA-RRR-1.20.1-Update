package com.whfwtf.taiga;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.event.level.BlockEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;

/**
 * 自定义特性的行为实现，逐条对齐实例内 kubejs/server_scripts/taiga_properties/*.js。
 *
 * <p>是否持有某特性通过工具 NBT（TinkerData.Modifiers.&lt;modifier id&gt;）判断，与 KJS 写法一致。
 */
public final class TaigaTraitEvents {

    public TaigaTraitEvents() {}

    /** 读取工具上某特性的等级（未持有为 0）。 */
    private static int level(ItemStack stack, String id) {
        CompoundTag root = stack.getTag();
        if (root == null) {
            return 0;
        }
        CompoundTag modifiers = root.getCompound("TinkerData").getCompound("Modifiers");
        return modifiers.getInt(TAIGA.MODID + ":" + id);
    }

    private static boolean has(ItemStack stack, String id) {
        return level(stack, id) > 0;
    }

    /** berserker：命中时伤害翻倍，并额外损耗 3 点耐久。 */
    @SubscribeEvent
    public void onBerserkerHurt(LivingHurtEvent event) {
        Entity source = event.getSource().getEntity();
        if (!(source instanceof Player player)) {
            return;
        }
        ItemStack tool = player.getMainHandItem();
        if (!has(tool, ModModifiers.BERSERKER)) {
            return;
        }
        event.setAmount(event.getAmount() * 2.0F);
        tool.hurtAndBreak(3, player, broken -> { });
    }

    /** soul_eater：击杀累计 SoulCount / BonusDmg（Δ = rand × maxHp × 100 / 25000，保留两位小数）。 */
    @SubscribeEvent
    public void onSoulEaterKill(LivingDeathEvent event) {
        Entity source = event.getSource().getEntity();
        if (!(source instanceof Player player)) {
            return;
        }
        ItemStack tool = player.getMainHandItem();
        if (!has(tool, ModModifiers.SOUL_EATER)) {
            return;
        }
        CompoundTag tag = tool.getOrCreateTag();
        int soulCount = tag.getInt("SoulCount");
        float bonus = tag.getFloat("BonusDmg");

        float maxHealth = event.getEntity().getMaxHealth();
        float delta = (float) (Math.random() * maxHealth * 100.0 / 25000.0);

        soulCount += 1;
        bonus = Math.round((bonus + delta) * 100.0F) / 100.0F;

        tag.putInt("SoulCount", soulCount);
        tag.putFloat("BonusDmg", bonus);
    }

    /** soul_eater：把累计的附加伤害加到本次伤害上。 */
    @SubscribeEvent
    public void onSoulEaterHurt(LivingHurtEvent event) {
        Entity source = event.getSource().getEntity();
        if (!(source instanceof Player player)) {
            return;
        }
        ItemStack tool = player.getMainHandItem();
        if (!has(tool, ModModifiers.SOUL_EATER)) {
            return;
        }
        CompoundTag tag = tool.getTag();
        if (tag == null) {
            return;
        }
        float bonus = tag.getFloat("BonusDmg");
        if (bonus > 0.0F) {
            event.setAmount(event.getAmount() + bonus);
        }
    }

    /** unstable：破坏方块时 3% 概率爆炸（强度 1.2~6.2）并额外损耗 2~11 耐久。 */
    @SubscribeEvent
    public void onUnstableBreak(BlockEvent.BreakEvent event) {
        Player player = event.getPlayer();
        ItemStack tool = player.getMainHandItem();
        if (!has(tool, ModModifiers.UNSTABLE)) {
            return;
        }
        if (Math.random() >= 0.03) {
            return;
        }
        float strength = (float) (1.2 + Math.random() * 5.0);
        if (event.getLevel() instanceof Level level) {
            level.explode(player, event.getPos().getX() + 0.5, event.getPos().getY() + 0.5,
                    event.getPos().getZ() + 0.5, strength, Level.ExplosionInteraction.TNT);
        }
        tool.hurtAndBreak(2 + (int) Math.floor(Math.random() * 10), player, broken -> { });
    }
}
