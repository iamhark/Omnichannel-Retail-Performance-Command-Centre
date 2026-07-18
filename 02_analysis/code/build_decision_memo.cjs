const fs = require('fs');
const path = require('path');
const {
  AlignmentType, BorderStyle, Document, Footer, HeadingLevel, LevelFormat,
  PageBreak, PageNumber, Packer, Paragraph, ShadingType, Table, TableCell,
  TableRow, TextRun, WidthType
} = require('docx');

const project = path.resolve(__dirname, '..', '..');
const out = path.join(project, '04_deliverables', 'review', '2026-07-18-omnichannel-retail-decision-memo-v1.docx');
const navy = '16324F';
const teal = '2A9D8F';
const light = 'EAF2F4';
const border = { style: BorderStyle.SINGLE, size: 4, color: 'C7D3D9' };
const borders = { top: border, bottom: border, left: border, right: border };

const p = (text, options = {}) => new Paragraph({
  spacing: { after: options.after ?? 100, line: 250 },
  alignment: options.alignment,
  border: options.border,
  children: [new TextRun({ text, bold: options.bold, size: options.size ?? 19, color: options.color ?? '202A30', font: 'Arial' })]
});

const bullet = (text) => new Paragraph({
  numbering: { reference: 'bullets', level: 0 },
  spacing: { after: 65, line: 235 },
  children: [new TextRun({ text, size: 18, font: 'Arial', color: '202A30' })]
});

const cell = (text, width, header = false) => new TableCell({
  width: { size: width, type: WidthType.DXA }, borders,
  shading: { fill: header ? navy : 'FFFFFF', type: ShadingType.CLEAR },
  margins: { top: 70, bottom: 70, left: 100, right: 100 },
  children: [new Paragraph({ children: [new TextRun({ text, bold: header, color: header ? 'FFFFFF' : '202A30', size: 16, font: 'Arial' })] })]
});

const finding = (number, title, evidence, action) => [
  new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 110, after: 55 },
    children: [new TextRun({ text: `${number}. ${title}`, bold: true, size: 22, color: navy, font: 'Arial' })]
  }),
  p(evidence, { after: 55 }),
  new Paragraph({
    spacing: { after: 90, line: 245 },
    border: { left: { style: BorderStyle.SINGLE, size: 14, color: teal, space: 8 } },
    children: [new TextRun({ text: 'Action: ', bold: true, size: 18, color: teal, font: 'Arial' }), new TextRun({ text: action, size: 18, color: '202A30', font: 'Arial' })]
  })
];

const doc = new Document({
  styles: {
    default: { document: { run: { font: 'Arial', size: 19 } } },
    paragraphStyles: [
      { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { size: 26, bold: true, font: 'Arial', color: navy }, paragraph: { spacing: { before: 120, after: 90 }, outlineLevel: 0 } },
      { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { size: 22, bold: true, font: 'Arial', color: navy }, paragraph: { spacing: { before: 100, after: 60 }, outlineLevel: 1 } }
    ]
  },
  numbering: { config: [{ reference: 'bullets', levels: [{ level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 330, hanging: 180 } } } }] }] },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 650, right: 720, bottom: 650, left: 720 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: 'Omnichannel Retail Performance Command Centre  |  ', size: 15, color: '66757F', font: 'Arial' }), new TextRun({ children: [PageNumber.CURRENT], size: 15, color: '66757F', font: 'Arial' })] })] }) },
    children: [
      new Paragraph({ border: { bottom: { style: BorderStyle.SINGLE, size: 18, color: teal, space: 6 } }, spacing: { after: 80 }, children: [new TextRun({ text: 'DECISION MEMO', bold: true, size: 18, color: teal, font: 'Arial' })] }),
      p('Omnichannel Retail Performance Command Centre', { bold: true, size: 31, color: navy, after: 40 }),
      p('To: Retail Executive Committee     From: Harkirat Singh     Date: 18 July 2026', { size: 16, color: '52646F', after: 80 }),
      p('Decision: Reallocate retention, store-diagnostic, and marketing attention using the validated business-case model.', { bold: true, size: 20, color: navy, after: 75 }),
      p('Basis: CC BY 4.0 UCI Online Retail transactions combined with deterministic simulated stores, costs, sessions, campaigns, and attribution. Store and marketing results are simulated business-case evidence, not observed company performance.', { size: 17, color: '52646F', after: 85 }),
      ...finding(1, 'Protect concentrated customer value; separate retention from reactivation',
        'Champions are 714 of 4,371 identified customers (16.3%) but generate 46.1% of monetary value and average £1,793 observed historical CLV. At Risk and Lost segments contain 1,335 customers (30.5%). In the unsimulated UCI core, 65.6% of 4,338 identified purchasing customers place at least two completed orders.',
        'Protect Champions with service and loyalty treatment. Run a capped reactivation test for At Risk customers; suppress Lost customers after two failed contacts.'),
      ...finding(2, 'Diagnose matched-store gaps before changing network-wide targets',
        'In the simulated large-store tier, Manchester is £94,542 (+18.0%) above its peer baseline while Birmingham is £94,542 (-18.0%) below. Leeds is £44,976 (+11.4%) above the standard-store baseline; Bristol is £27,233 (-6.9%) below.',
        'Compare each matched pair on category mix, returns, conversion, discounting, and staffing. Transfer only practices that survive those checks.'),
      ...finding(3, 'Stop simulated Social spend from absorbing margin',
        'Simulated Social produces -47.0% ROI and £421 acquisition cost. Email produces +52.4% ROI at £168 per conversion; Paid Search produces +51.1% at £165.',
        'Reduce Social prospecting in the next simulated planning cycle, move the test budget to Email and Paid Search, and preserve a Social holdout.'),
      new Paragraph({ children: [new PageBreak()] }),
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun('Limitations')] }),
      bullet('The public source is historical and online-only; it does not represent current retail conditions.'),
      bullet('Physical stores, costs, categories, sessions, campaigns, spend, and attribution are simulated.'),
      bullet('Last non-direct attribution assigns credit; it does not estimate causal lift.'),
      bullet('Customer IDs are missing for 135,080 raw rows, so customer metrics exclude anonymous transactions.'),
      bullet('December 2011 contains nine days and is excluded from complete-month comparisons.'),
      bullet('DAX-to-SQL reconciliation covers six scenarios; other filter combinations remain untested.'),
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun('Metrics to monitor')] }),
      new Table({
        width: { size: 10466, type: WidthType.DXA }, columnWidths: [2150, 5166, 1500, 1650],
        rows: [
          new TableRow({ children: [cell('Decision area', 2150, true), cell('Metrics', 5166, true), cell('Cadence', 1500, true), cell('Trigger', 1650, true)] }),
          new TableRow({ children: [cell('Customer value', 2150), cell('Retention, repeat rate, segment migration, CLV, contribution/customer', 5166), cell('Monthly', 1500), cell('Two declines', 1650)] }),
          new TableRow({ children: [cell('Store operations', 2150), cell('Revenue, margin rate, returns, peer variance by format/category', 5166), cell('Weekly/monthly', 1500), cell('Two negative periods', 1650)] }),
          new TableRow({ children: [cell('Marketing', 2150), cell('Spend, conversion, CAC, attributed revenue, ROAS, ROI, holdout lift', 5166), cell('Weekly/close', 1500), cell('ROI < 0 or CAC > contribution', 1650)] })
        ]
      }),
      p('Evidence: CLM-002 to CLM-008 in 03_synthesis/evidence-register.md. Computed tables are under 02_analysis/outputs/tables/.', { size: 16, color: '52646F', after: 55 }),
      p('Source: Chen, D. (2015). Online Retail [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5BW33. CC BY 4.0.', { size: 16, color: '52646F', after: 40 })
    ]
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.mkdirSync(path.dirname(out), { recursive: true });
  fs.writeFileSync(out, buffer);
  console.log(out);
});
