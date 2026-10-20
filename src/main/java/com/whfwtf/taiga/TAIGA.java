package com.whfwtf.taiga;

import com.mojang.logging.LogUtils;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.event.level.BlockEvent;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import org.slf4j.Logger;

/**
 * TAIGA（1.20.1 移植 / taiga3）
 */
@Mod(TAIGA.MODID)
public class TAIGA {

    public static final String MODID = "taiga";
    public static final Logger LOGGER = LogUtils.getLogger();

    public TAIGA() {
        IEventBus modBus = FMLJavaModLoadingContext.get().getModEventBus();

        ModItems.register();
        ModBlocks.register();
        ModFluids.register();

        ModItems.ITEMS.register(modBus);
        ModBlocks.BLOCKS.register(modBus);
        ModFluids.FLUID_TYPES.register(modBus);
        ModFluids.FLUIDS.register(modBus);
        ModFluids.FLUID_BLOCKS.register(modBus);

        ModCreativeTabs.TABS.register(modBus);
        // 特性由数据包 JSON 定义，无需（也不能）注册静态 Modifier

        MinecraftForge.EVENT_BUS.register(this);
        MinecraftForge.EVENT_BUS.register(new TaigaTraitEvents());

        LOGGER.info("TAIGA 1.20.1 (taiga3) loaded");
    }

    /**
     * 与 kubejs server_scripts/taiga 行为一致：
     * - 泰伯利亚矿石被破坏时 10% 概率爆炸
     * - 陨铁原矿块被破坏时变为陨石圆石块
     */
    @SubscribeEvent
    public void onBlockBreak(BlockEvent.BreakEvent event) {
        Level level = (Level) event.getLevel();
        Block broken = event.getState().getBlock();

        if (broken == block("raw_meteorite_block")) {
            event.setCanceled(true);
            level.setBlockAndUpdate(event.getPos(), block("meteorite_cobble_block").defaultBlockState());
            return;
        }

        if (broken == block("tiberium_ore") && level.random.nextFloat() <= 0.1F) {
            level.explode(event.getPlayer(), event.getPos().getX() + 0.5, event.getPos().getY() + 0.5,
                    event.getPos().getZ() + 0.5, 2.0F, Level.ExplosionInteraction.TNT);
        }
    }

    private static Block block(String name) {
        return ModBlocks.all().get(name).get();
    }
}
