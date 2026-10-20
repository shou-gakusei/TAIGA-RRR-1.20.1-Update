package com.whfwtf.taiga;

import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Block;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.RegistryObject;

/**
 * 创造模式标签页：TAIGA 物品 / TAIGA 方块。
 */
public final class ModCreativeTabs {

    public static final DeferredRegister<CreativeModeTab> TABS =
            DeferredRegister.create(Registries.CREATIVE_MODE_TAB, TAIGA.MODID);

    public static final RegistryObject<CreativeModeTab> ITEMS = TABS.register("items", () ->
            CreativeModeTab.builder()
                    .title(Component.translatable("itemGroup.taiga.items"))
                    .icon(() -> new ItemStack(ModItems.all().get("adamant_ingot").get()))
                    .displayItems((params, output) -> ModItems.all().forEach((name, ro) -> {
                        if (!ModBlocks.all().containsKey(name)) {
                            output.accept(ro.get());
                        }
                    }))
                    .build());

    public static final RegistryObject<CreativeModeTab> BLOCKS = TABS.register("blocks", () ->
            CreativeModeTab.builder()
                    .title(Component.translatable("itemGroup.taiga.blocks"))
                    .icon(() -> new ItemStack(ModBlocks.all().get("adamant_block").get()))
                    .displayItems((params, output) -> ModBlocks.all().forEach((name, ro) -> {
                        Block block = ro.get();
                        output.accept(block);
                    }))
                    .build());

    private ModCreativeTabs() {}
}
