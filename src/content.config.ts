import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

// Astro 6 内容层 API：用 glob loader 替代旧 type: 'content'
// 字段与旧 Jekyll front matter 一一对应
const blog = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/blog' }),
  schema: z.object({
    title: z.string(),
    subtitle: z.string().optional(),
    date: z.coerce.date(),
    author: z.string().default('沐杰'),
    'header-img': z.string().optional(),
    tags: z.array(z.string()).default([]),
    catalog: z.boolean().default(false),
    legacySlug: z.string().optional(),
  }),
});

export const collections = { blog };
