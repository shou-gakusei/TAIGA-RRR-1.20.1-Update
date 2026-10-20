package com.whfwtf.taiga;

import net.minecraft.world.item.Item;
import net.minecraft.world.item.PickaxeItem;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

import javax.annotation.Nullable;
import java.util.LinkedHashMap;
import java.util.Map;

/**
 * 物品注册：37 材料 × 锭/粒/粉 + 晶体与粗矿 + 镐子。
 * （方块物品由 {@link ModBlocks} 一并注册进本类的 ITEMS）
 */
public final class ModItems {

    public static final DeferredRegister<Item> ITEMS =
            DeferredRegister.create(ForgeRegistries.ITEMS, TAIGA.MODID);

    private static final Map<String, RegistryObject<Item>> ALL = new LinkedHashMap<>();

    /** 原矿/晶体物品（与 tooltips/gen_content.py 的 RAW_ITEMS 一致） */
    public static final String[] RAW_ITEMS = {
            "dilithium_crystal", "raw_abyssum", "raw_aurorium", "raw_duranite", "raw_eezo",
            "raw_jauxum", "raw_karmesine", "raw_osram", "raw_ovium", "raw_palladium",
            "raw_prometheum", "raw_uru", "raw_valyrium", "raw_vibranium", "tiberium_crystal"
    };

    public static final String[] TOOLS = {"dyonite", "nucleum", "solarium"};

    private ModItems() {}

    static RegistryObject<Item> add(String name, RegistryObject<Item> ro) {
        ALL.put(name, ro);
        return ro;
    }

    public static void register() {
        for (ModMaterials.Def m : ModMaterials.ALL) {
            simple(m.name() + "_ingot");
            simple(m.name() + "_nugget");
            simple(m.name() + "_dust");
        }
        for (String raw : RAW_ITEMS) {
            simple(raw);
        }
        simple("random_ore");
        for (String tool : TOOLS) {
            add(tool + "_pickaxe", ITEMS.register(tool + "_pickaxe", () ->
                    new PickaxeItem(TaigaTiers.of(tool), 1, -2.8F,
                            new Item.Properties().durability(durability(tool)))));
        }
    }

    private static void simple(String name) {
        add(name, ITEMS.register(name, () -> new Item(new Item.Properties())));
    }

    private static int durability(String tool) {
        return switch (tool) {
            case "dyonite" -> 500;
            case "nucleum" -> 1000;
            default -> 1500;
        };
    }

    @Nullable
    public static Item get(String name) {
        RegistryObject<Item> ro = ALL.get(name);
        return ro == null ? null : ro.get();
    }

    public static Map<String, RegistryObject<Item>> all() {
        return ALL;
    }
}
