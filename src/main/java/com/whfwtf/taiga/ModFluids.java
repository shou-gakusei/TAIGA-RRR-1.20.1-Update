package com.whfwtf.taiga;

import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.BucketItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.LiquidBlock;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.FlowingFluid;
import net.minecraftforge.client.extensions.common.IClientFluidTypeExtensions;
import net.minecraftforge.fluids.ForgeFlowingFluid;
import net.minecraftforge.fluids.FluidType;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.function.Consumer;

/**
 * 流体注册：37 材料熔融液 + 硝化合金 + 烈焰哈瓦。
 * 颜色与温度来自 {@link ModMaterials}（与 kubejs taiga_fluids.js 同源）。
 */
public final class ModFluids {

    public static final DeferredRegister<FluidType> FLUID_TYPES =
            DeferredRegister.create(ForgeRegistries.Keys.FLUID_TYPES, TAIGA.MODID);
    public static final DeferredRegister<net.minecraft.world.level.material.Fluid> FLUIDS =
            DeferredRegister.create(ForgeRegistries.FLUIDS, TAIGA.MODID);
    public static final DeferredRegister<net.minecraft.world.level.block.Block> FLUID_BLOCKS =
            DeferredRegister.create(ForgeRegistries.BLOCKS, TAIGA.MODID);

    private static final ResourceLocation STILL = new ResourceLocation("minecraft", "block/water_still");
    private static final ResourceLocation FLOWING = new ResourceLocation("minecraft", "block/water_flow");

    private static final Map<String, RegistryObject<FlowingFluid>> SOURCES = new HashMap<>();
    private static final Map<String, RegistryObject<FlowingFluid>> FLOWINGS = new HashMap<>();
    private static final Map<String, RegistryObject<LiquidBlock>> BLOCKS = new HashMap<>();
    private static final Map<String, RegistryObject<Item>> BUCKETS = new HashMap<>();

    /** 供创造标签使用的全部流体（源） */
    public static final Map<String, RegistryObject<FlowingFluid>> ALL = new LinkedHashMap<>();

    private ModFluids() {}

    public static void register() {
        for (ModMaterials.Def m : ModMaterials.ALL) {
            own("molten_" + m.name(), "molten_" + m.name(), m.color(), m.temperature());
        }
        own("molten_nitronite", "molten_nitronite", 0xA6D000, 300);
        own("blaze_halwa", "blaze_halwa", 0xEC8B35, 300);
    }

    private static void own(String id, String langKey, int color, int temperature) {
        RegistryObject<FluidType> type = FLUID_TYPES.register(id, () -> new FluidType(
                FluidType.Properties.create()
                        .descriptionId("fluid_type.taiga." + langKey)
                        .density(2000)
                        .viscosity(8000)
                        .temperature(temperature)) {
            @Override
            public void initializeClient(Consumer<IClientFluidTypeExtensions> consumer) {
                consumer.accept(new IClientFluidTypeExtensions() {
                    @Override public ResourceLocation getStillTexture() { return STILL; }
                    @Override public ResourceLocation getFlowingTexture() { return FLOWING; }
                    @Override public int getTintColor() { return 0xFF000000 | color; }
                });
            }
        });

        RegistryObject<FlowingFluid> still = FLUIDS.register(id, () ->
                new ForgeFlowingFluid.Source(properties(id, type)));
        SOURCES.put(id, still);
        RegistryObject<FlowingFluid> flowing = FLUIDS.register("flowing_" + id, () ->
                new ForgeFlowingFluid.Flowing(properties(id, type)));
        FLOWINGS.put(id, flowing);

        BLOCKS.put(id, FLUID_BLOCKS.register(id, () ->
                new LiquidBlock(still.get(), BlockBehaviour.Properties.copy(Blocks.WATER).noLootTable())));
        BUCKETS.put(id, ModItems.ITEMS.register(id + "_bucket", () ->
                new BucketItem(still, new Item.Properties().craftRemainder(Items.BUCKET).stacksTo(1))));

        ALL.put(id, still);
    }

    /** 在流体源/流动流体的 supplier 被求值时才构造 Properties，此时各映射表已填好。 */
    private static ForgeFlowingFluid.Properties properties(String id, RegistryObject<FluidType> type) {
        ForgeFlowingFluid.Properties p = new ForgeFlowingFluid.Properties(type, SOURCES.get(id), FLOWINGS.get(id));
        RegistryObject<LiquidBlock> block = BLOCKS.get(id);
        if (block != null) {
            p.block(block);
        }
        RegistryObject<Item> bucket = BUCKETS.get(id);
        if (bucket != null) {
            p.bucket(bucket);
        }
        return p;
    }
}
