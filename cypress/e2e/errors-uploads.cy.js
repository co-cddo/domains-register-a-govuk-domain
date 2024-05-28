import './base.cy'

describe('Errors when uploading files', () => {
  it('Complains when the exemption file has a problem', () => {

    cy.goToExemptionUpload()

    // don't select a file but click
    cy.get('.govuk-button#id_submit').click()

    cy.confirmProblem('Choose the file you want to upload.')

    // select a too big file
    cy.uploadDocument('large-image.png')

    cy.confirmProblem('Please keep filesize under')

    // select not an image
    cy.uploadDocument('example.json')
    cy.confirmProblem('Wrong file format.')

    // do it right this time
    cy.uploadDocument('exemption.png')
    cy.checkPageTitleIncludes('Confirm uploaded evidence of the exemption')
    cy.get('.govuk-tag').should('include.text', 'Uploaded')
  })

  it('Complains when the permission file has a problem', () => {

    cy.goToWrittenPermissionUpload()

    // don't select a file but click
    cy.get('.govuk-button#id_submit').click()

    cy.confirmProblem('Choose the file you want to upload.')

    // select a too big file
    cy.uploadDocument('large-image.png')

    cy.confirmProblem('Please keep filesize under')

    // select not an image
    cy.uploadDocument('example.json')
    cy.confirmProblem('Wrong file format.')

    // do it right this time
    cy.uploadDocument('permission.png')
    cy.checkPageTitleIncludes('Confirm uploaded evidence of permission to apply')
    cy.get('.govuk-tag').should('include.text', 'Uploaded')
  })

  it('Complains when the minister file has a problem', () => {

    cy.goToMinisterUpload()

    // don't select a file but click
    cy.get('.govuk-button#id_submit').click()

    cy.confirmProblem('Choose the file you want to upload.')

    // select a too big file
    cy.uploadDocument('large-image.png')

    cy.confirmProblem('Please keep filesize under')

    // select not an image
    cy.uploadDocument('example.json')
    cy.confirmProblem('Wrong file format.')

    // do it right this time
    cy.uploadDocument('minister.png')
    cy.checkPageTitleIncludes('Confirm uploaded evidence of the minister\'s request')
    cy.get('.govuk-tag').should('include.text', 'Uploaded')
  })

})
