import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'OpenEVSE for Home Assistant',
  description: 'Smart, local electric vehicle charging integration for Home Assistant',
  base: '/openevse/',
  cleanUrls: true,
  lastUpdated: true,

  head: [
    ['link', { rel: 'icon', type: 'image/svg+xml', href: '/openevse/favicon.svg' }],
    ['meta', { name: 'theme-color', content: '#0284c7' }],
    ['meta', { property: 'og:type', content: 'website' }],
    ['meta', { property: 'og:title', content: 'OpenEVSE Integration for Home Assistant' }],
    ['meta', { property: 'og:description', content: 'Direct, local control and energy monitoring for OpenEVSE EV chargers in Home Assistant.' }],
  ],

  themeConfig: {
    logo: { src: '/logo.svg', alt: 'OpenEVSE Logo' },
    siteTitle: 'OpenEVSE HA',

    nav: [
      { text: 'Guide', link: '/getting-started' },
      { text: 'Features', link: '/features' },
      { text: 'Services', link: '/services' },
      { text: 'Entities', link: '/entities' },
      { text: 'FAQ & Troubleshooting', link: '/troubleshooting' },
      {
        text: 'Links',
        items: [
          { text: 'OpenEVSE Hardware', link: 'https://openevse.com' },
          { text: 'OpenEVSE Lovelace Card', link: 'https://github.com/KipK/openevse-card' },
          { text: 'Home Assistant Community', link: 'https://community.home-assistant.io/' },
          { text: 'Discord Community', link: 'https://discord.gg/Qa5fW2R' },
        ]
      }
    ],

    sidebar: [
      {
        text: 'Getting Started',
        items: [
          { text: 'Introduction', link: '/getting-started' },
          { text: 'Installation (HACS & Manual)', link: '/installation' },
          { text: 'Configuration', link: '/configuration' },
        ]
      },
      {
        text: 'Features & Capabilities',
        items: [
          { text: 'Overview', link: '/features' },
          { text: 'Solar PV Divert', link: '/features#solar-pv-divert-mode' },
          { text: 'Claims & Manual Overrides', link: '/features#claim-and-override-system' },
          { text: 'RFID Card Management', link: '/features#rfid-management-v4-0-v5-0' },
          { text: 'Firmware Updates', link: '/features#firmware-updates' },
          { text: 'Energy Dashboard', link: '/features#home-assistant-energy-dashboard' },
        ]
      },
      {
        text: 'Reference',
        items: [
          { text: 'Platforms & Entities', link: '/entities' },
          { text: 'Service Calls Reference', link: '/services' },
          { text: 'Lovelace UI & Cards', link: '/dashboards' },
        ]
      },
      {
        text: 'Help & Development',
        items: [
          { text: 'Troubleshooting & FAQ', link: '/troubleshooting' },
          { text: 'Contributing', link: '/contributing' },
        ]
      }
    ],

    socialLinks: [
      { icon: 'github', link: 'https://github.com/firstof9/openevse' },
      { icon: 'discord', link: 'https://discord.gg/Qa5fW2R' }
    ],

    search: {
      provider: 'local'
    },

    editLink: {
      pattern: 'https://github.com/firstof9/openevse/edit/main/docs/:path',
      text: 'Edit this page on GitHub'
    },

    footer: {
      message: 'Released under the MIT License.',
      copyright: 'Maintained by Chris Nowak (@firstof9) & Contributors'
    }
  }
})
