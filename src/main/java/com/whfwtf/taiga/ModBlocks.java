package com.whfwtf.taiga;

import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

import java.util.LinkedHashMap;
import java.util.Map;

/**
 * 方块注册：37 金属块 + 15 矿石 + 15 粗矿块 + 5 特殊块（含方块物品）。
 */
public final class ModBlocks {

    public static final DeferredRegister<Block> BLOCKS =
            DeferredRegister.create(ForgeRegistries.BLOCKS, TAIGA.MODID);

    private static final Map<String, RegistryObject<Block>> ALL = new LinkedHashMap<>();

    /** 有矿石方块的 15 种材料（与 gen_content.py 的 ORE_MATS 一致） */
    public static final String[] ORES = {
            "abyssum", "aurorium", "dilithium", "eezo", "jauxum",
            "karmesine", "osram", "ovium", "tiberium",
            "duranite", "prometheum", "palladium", "uru", "valyrium", "vibranium"
    };

    /** 特殊方块（与 gen_content.py 的 SPECIAL_BLOCKS 一致） */
    public static final String[] SPECIAL = {
            "basalt_rock", "meteorite_cobble_block", "raw_meteorite_block",
            "raw_obsidiorite_block", "obsidiorite_cobble_block"
    };

    private ModBlocks() {}

    private static void stone(String name) {
        RegistryObject<Block> ro = BLOCKS.register(name, () -> new Block(
                BlockBehaviour.Properties.of()
                        .mapColor(MapColor.STONE)
                        .strength(3.0F, 3.0F)
                        .requiresCorrectToolForDrops()
                        .sound(SoundType.STONE)));
        ALL.put(name, ro);
        ModItems.add(name, ModItems.ITEMS.register(name, () -> new BlockItem(ro.get(), new Item.Properties())));
    }

    public static void register() {
        for (ModMaterials.Def m : ModMaterials.ALL) {
            stone(m.name() + "_block");
        }
        for (String ore : ORES) {
            stone(ore + "_ore");
        }
        for (String raw : ModItems.RAW_ITEMS) {
            stone(raw + "_block");
        }
        for (String special : SPECIAL) {
            stone(special);
        }
    }

    public static Map<String, RegistryObject<Block>> all() {
        return ALL;
    }
}
