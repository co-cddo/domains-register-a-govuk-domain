import './base.cy'

describe('Errors when uploading files', () => {
  it('Rejects files that are too big', () => {

    cy.goToExemptionUpload()
    cy.uploadDocument('large-image.png')

    cy.checkPageTitleIncludes('Upload evidence of the exemption')
    cy.confirmProblem('Please keep filesize under 2.5\u00a0MB. Current filesize 2.9\u00a0MB')

    cy.uploadDocument('image.png')
    cy.confirmUpload('image.png')
  })

  it('Rejects files that are not images', () => {

    cy.goToExemptionUpload()
    cy.uploadDocument('example.json')

    cy.checkPageTitleIncludes('Upload evidence of the exemption')
    cy.confirmProblem('Wrong file format. Please upload an image.')

    cy.uploadDocument('image.png')
    cy.confirmUpload('image.png')
  })
});
