//! Standards-derived artefact recipes, semantic scenes and deterministic renderers.
#![forbid(unsafe_code)]

pub mod prisma;
pub mod recipe;
pub mod render;
pub mod scene;

pub use prisma::{
    DatabaseRegisterStream, ExclusionReason, IncludedCounts, OtherMethodsStream, PrismaError,
    PrismaFlow, PrismaTemplate, parse_prisma_flow,
};
pub use recipe::{
    AccessibilityContract, ArtifactType, DiagramRecipe, GridLayout, RecipeEdge, RecipeError,
    RecipeNode, RecipeOutput,
};
pub use render::{RenderError, RenderFormat, render, render_scene_json, render_svg, render_text};
pub use scene::{Anchor, Canvas, EdgeKind, NodeRole, Point, Rect, Scene, SceneEdge, SceneNode};
