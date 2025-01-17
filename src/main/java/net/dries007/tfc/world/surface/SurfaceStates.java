/*
 * Licensed under the EUPL, Version 1.2.
 * You may obtain a copy of the Licence at:
 * https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12
 */

package net.dries007.tfc.world.surface;

import java.util.function.Supplier;

import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.material.Fluids;

import net.dries007.tfc.common.blocks.SandstoneBlockType;
import net.dries007.tfc.common.blocks.TFCBlocks;
import net.dries007.tfc.common.blocks.soil.SandBlockType;
import net.dries007.tfc.common.blocks.soil.SoilBlockType;
import net.dries007.tfc.common.fluids.TFCFluids;

public class SurfaceStates
{
    public static final SurfaceState RAW = context -> context.getRock().raw().defaultBlockState();
    public static final SurfaceState COBBLE = context -> context.getRock().cobble().defaultBlockState();
    public static final SurfaceState GRAVEL = context -> context.getRock().gravel().defaultBlockState();

    /**
     * Grass / Dirt / Gravel, or Sand / Sand / Sandstone
     */
    public static final SurfaceState TOP_SOIL = new SoilSurfaceState(SoilBlockType.GRASS);
    public static final SurfaceState MID_SOIL = new SoilSurfaceState(SoilBlockType.DIRT);
    public static final SurfaceState LOW_SOIL = new DeepSoilSurfaceState();

    public static final SurfaceState TOP_UNDERWATER = new UnderwaterSurfaceState(false);
    public static final SurfaceState LOW_UNDERWATER = new UnderwaterSurfaceState(true);

    public static final SurfaceState SHORE_SAND = context -> context.getBottomRock().sand().defaultBlockState();
    public static final SurfaceState SHORE_SANDSTONE = context -> context.getBottomRock().sandstone().defaultBlockState();

    public static final SurfaceState RARE_SHORE_SAND = new SurfaceState()
    {
        private final Supplier<Block> pinkSand = TFCBlocks.SAND.get(SandBlockType.PINK);
        private final Supplier<Block> blackSand = TFCBlocks.SAND.get(SandBlockType.BLACK);

        @Override
        public BlockState getState(SurfaceBuilderContext context)
        {
            if (context.rainfall() > 300f && context.averageTemperature() > 15f)
            {
                return pinkSand.get().defaultBlockState();
            }
            else if (context.rainfall() > 300f)
            {
                return blackSand.get().defaultBlockState();
            }
            else
            {
                return context.getBottomRock().sand().defaultBlockState();
            }
        }
    };

    public static final SurfaceState RARE_SHORE_SANDSTONE = new SurfaceState()
    {
        private final Supplier<Block> pinkSandstone = TFCBlocks.SANDSTONE.get(SandBlockType.PINK).get(SandstoneBlockType.RAW);
        private final Supplier<Block> blackSandstone = TFCBlocks.SANDSTONE.get(SandBlockType.BLACK).get(SandstoneBlockType.RAW);

        @Override
        public BlockState getState(SurfaceBuilderContext context)
        {
            if (context.rainfall() > 300f && context.averageTemperature() > 15f)
            {
                return pinkSandstone.get().defaultBlockState();
            }
            else if (context.rainfall() > 300f)
            {
                return blackSandstone.get().defaultBlockState();
            }
            else
            {
                return context.getBottomRock().sandstone().defaultBlockState();
            }
        }
    };

    public static final SurfaceState WATER = context -> context.salty() ?
        TFCFluids.SALT_WATER.getSourceBlock() :
        Fluids.WATER.defaultFluidState().createLegacyBlock();
}
