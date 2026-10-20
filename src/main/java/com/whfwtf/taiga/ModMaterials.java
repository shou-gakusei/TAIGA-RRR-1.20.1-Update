package com.whfwtf.taiga;

import java.util.Arrays;
import java.util.List;

/**
 * 材料总表——由 tools/gen_content.py 从 kubejs/taiga_fluids.js 生成，请勿手改。
 */
public final class ModMaterials {
    public record Def(String name, int color, int temperature) {}

    public static final List<Def> ALL = Arrays.asList(
            new Def("abyssum", 0x105B5E, 300),
            new Def("adamant", 0xCC72CB, 300),
            new Def("astrium", 0x752E4D, 300),
            new Def("aurorium", 0x735447, 300),
            new Def("basalt", 0xF7F3DF, 300),
            new Def("dilithium", 0x608A84, 300),
            new Def("duranite", 0x536B71, 1450),
            new Def("dyonite", 0xD49D34, 300),
            new Def("eezo", 0x405865, 300),
            new Def("fractum", 0x8F8659, 300),
            new Def("ignitz", 0x8E162A, 300),
            new Def("imperomite", 0x68C382, 300),
            new Def("iox", 0x55AA55, 300),
            new Def("jauxum", 0x608A84, 300),
            new Def("karmesine", 0xCD3F40, 300),
            new Def("lumix", 0x9B8772, 300),
            new Def("meteorite", 0x2C3F31, 300),
            new Def("nihilite", 0x31215A, 1800),
            new Def("niob", 0x3C4F60, 1450),
            new Def("nucleum", 0xCCE239, 1450),
            new Def("obsidiorite", 0x1B3A42, 300),
            new Def("osram", 0xAE8062, 300),
            new Def("ovium", 0x413E66, 300),
            new Def("palladium", 0x9E5924, 300),
            new Def("prometheum", 0x251D31, 300),
            new Def("proxii", 0x8DAD9A, 1450),
            new Def("seismum", 0xCCA291, 300),
            new Def("solarium", 0xDDD857, 1800),
            new Def("terrax", 0x877B74, 300),
            new Def("tiberium", 0xADD000, 300),
            new Def("triberium", 0x39861E, 300),
            new Def("tritonite", 0x59F5AB, 300),
            new Def("uru", 0x9B7A9E, 1450),
            new Def("valyrium", 0x81331B, 1800),
            new Def("vibranium", 0xA0B5BB, 1800),
            new Def("violium", 0x6D6784, 300),
            new Def("yrdeen", 0x632742, 1450)
    );
}
