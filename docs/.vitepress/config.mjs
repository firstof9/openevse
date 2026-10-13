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
      { text: 'Entities', link: '/entities' },
      { text: 'Services', link: '/services' },
      { text: 'Architecture', link: '/architecture' },
      { text: 'Troubleshooting', link: '/troubleshooting' },
      {
        text: 'External',
        items: [
          { text: 'OpenEVSE Official Site', link: 'https://openevse.com' },
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
          { text: 'Configuration & Certificates', link: '/configuration' },
        ]
      },
      {
        text: 'Smart Charging Features',
        items: [
          { text: 'Overview', link: '/features' },
          { text: 'Solar PV Divert & Current Shaper', link: '/solar-divert' },
          { text: 'Scheduling & Calendar', link: '/scheduling' },
          { text: 'RFID Management', link: '/rfid' },
          { text: 'Firmware Updates', link: '/firmware' },
        ]
      },
      {
        text: 'Reference',
        items: [
          { text: 'Entities & Platforms', link: '/entities' },
          { text: 'Service Calls Reference', link: '/services' },
          { text: 'Lovelace UI & Dashboards', link: '/dashboards' },
        ]
      },
      {
        text: 'Developer & Architecture',
        items: [
          { text: 'Internal Architecture', link: '/architecture' },
          { text: 'Contributing Guidelines', link: '/contributing' },
          { text: 'Troubleshooting & FAQ', link: '/troubleshooting' },
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
