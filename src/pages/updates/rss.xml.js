import rss from '@astrojs/rss';
import updatesData from '../../data/updates.json';

export function GET(context) {
  const items = [...updatesData.updates]
    .sort((a, b) => (a.date < b.date ? 1 : -1))
    .map((u) => ({
      title: u.title,
      description: u.summary,
      pubDate: new Date(u.date + 'T00:00:00Z'),
      link: u.url && u.url.startsWith('http') ? u.url : new URL(u.url || '/updates.html', context.site).href,
      categories: u.tags || [],
    }));

  return rss({
    title: 'Peterson Quantum Sensing — Development Updates',
    description:
      'Ongoing development at Peterson Quantum Sensing: validation milestones, publications, partnerships, and platform work.',
    site: context.site,
    items,
  });
}
